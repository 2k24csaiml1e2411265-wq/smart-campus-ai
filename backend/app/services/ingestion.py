from datetime import timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.ml.anomaly_detection import detect
from app.ml.recommendations import from_anomaly
from app.models.anomaly import Anomaly, AnomalySeverity, AnomalyStatus
from app.models.device import DeviceStatus
from app.models.readings import EnergyReading, EnvironmentReading, SolarReading, WaterReading
from app.services.lookups import department_by_code, device_by_external_id
from app.services.realtime import cache_clear, runtime_state, ws_manager
from app.utils.logging import logger
from app.utils.time import utcnow


def _touch_device(db: Session, device_id: str, value: float | None) -> tuple:
    device = device_by_external_id(db, device_id)
    if not device:
        return None, None
    device.last_seen = utcnow()
    device.status = DeviceStatus.online
    if value is not None:
        device.last_value = value
    return device, device.department_id


def ingest_energy(db: Session, payload: dict, broadcast: bool = True) -> dict:
    dept = department_by_code(db, payload["department"])
    if not dept:
        raise ValueError(f"Unknown department {payload['department']}")
    device, _ = _touch_device(db, payload["device_id"], payload.get("energy_kwh"))
    if not device:
        raise ValueError(f"Unknown device {payload['device_id']}")
    ts = payload.get("timestamp") or utcnow()
    reading = EnergyReading(
        device_id=device.id,
        department_id=dept.id,
        timestamp=ts,
        energy_kwh=payload["energy_kwh"],
        voltage=payload["voltage"],
        current=payload["current"],
        power_factor=payload["power_factor"],
        temperature=payload["temperature"],
        occupancy=payload["occupancy"],
        is_simulated=payload.get("is_simulated", True),
        is_anomaly_injected=payload.get("is_anomaly_injected", False),
    )
    db.add(reading)
    db.commit()
    runtime_state["last_ingest"] = utcnow().isoformat()
    runtime_state["simulator"] = "running"

    history_rows = db.execute(
        select(EnergyReading)
        .where(EnergyReading.department_id == dept.id, EnergyReading.timestamp >= ts - timedelta(hours=36))
        .order_by(EnergyReading.timestamp.asc())
    ).scalars().all()
    history = [
        {
            "timestamp": r.timestamp,
            "energy_kwh": r.energy_kwh,
            "occupancy": r.occupancy,
            "temperature": r.temperature,
            "solar_generation": 0.0,
        }
        for r in history_rows[:-1]
    ]
    latest = {
        "timestamp": reading.timestamp,
        "energy_kwh": reading.energy_kwh,
        "occupancy": reading.occupancy,
        "temperature": reading.temperature,
        "solar_generation": 0.0,
        "department": dept.code,
    }
    result = detect(dept.code, history, latest)
    anomaly_row = None
    if result.is_anomaly or payload.get("is_anomaly_injected"):
        if payload.get("is_anomaly_injected") and not result.is_anomaly:
            result.is_anomaly = True
            result.severity = "high"
        anomaly_row = Anomaly(
            department_id=dept.id,
            timestamp=ts,
            metric="energy",
            actual_value=result.actual,
            expected_value=result.expected,
            anomaly_score=result.anomaly_score,
            severity=AnomalySeverity(result.severity),
            reason=result.reason,
            recommendation=result.recommendation,
            status=AnomalyStatus.open,
        )
        db.add(anomaly_row)
        db.commit()
        db.refresh(anomaly_row)
        logger.info(
            "anomaly_detected",
            department=dept.code,
            score=result.anomaly_score,
            severity=result.severity,
        )

    cache_clear()
    event = {
        "type": "energy",
        "department": dept.code,
        "device_id": payload["device_id"],
        "energy_kwh": reading.energy_kwh,
        "timestamp": ts.isoformat() if hasattr(ts, "isoformat") else str(ts),
        "data_mode": "DEMO" if reading.is_simulated else "LIVE_SENSOR",
        "anomaly": None,
    }
    if anomaly_row:
        event["anomaly"] = {
            "id": anomaly_row.id,
            "department": dept.code,
            "actual": result.actual,
            "expected": result.expected,
            "anomaly_score": result.anomaly_score,
            "severity": result.severity,
            "reason": result.reason,
            "recommendation": result.recommendation,
        }
        rec = from_anomaly(
            dept.code,
            ((result.actual - result.expected) / result.expected * 100) if result.expected else 0,
            result.severity,
            ts.hour if hasattr(ts, "hour") else 12,
            result.contributing,
        )
        event["recommendation"] = rec
    if broadcast:
        try:
            import asyncio

            loop = asyncio.get_event_loop()
            if loop.is_running():
                loop.create_task(ws_manager.broadcast(event))
        except Exception:
            logger.info("ws_broadcast_skipped")
    return event


def ingest_solar(db: Session, payload: dict) -> None:
    dept = department_by_code(db, payload["department"])
    device, _ = _touch_device(db, payload["device_id"], payload.get("solar_kwh"))
    if not dept or not device:
        raise ValueError("Unknown department or device")
    db.add(
        SolarReading(
            device_id=device.id,
            department_id=dept.id,
            timestamp=payload.get("timestamp") or utcnow(),
            solar_kwh=payload["solar_kwh"],
            voltage=payload["voltage"],
            current=payload["current"],
            irradiance=payload["irradiance"],
            is_simulated=payload.get("is_simulated", True),
        )
    )
    db.commit()
    runtime_state["last_ingest"] = utcnow().isoformat()
    cache_clear()


def ingest_water(db: Session, payload: dict) -> None:
    dept = department_by_code(db, payload["department"])
    device, _ = _touch_device(db, payload["device_id"], payload.get("water_litres"))
    if not dept or not device:
        raise ValueError("Unknown department or device")
    db.add(
        WaterReading(
            device_id=device.id,
            department_id=dept.id,
            timestamp=payload.get("timestamp") or utcnow(),
            water_litres=payload["water_litres"],
            flow_rate=payload["flow_rate"],
            pressure=payload["pressure"],
            is_simulated=payload.get("is_simulated", True),
            is_anomaly_injected=payload.get("is_anomaly_injected", False),
        )
    )
    db.commit()
    runtime_state["last_ingest"] = utcnow().isoformat()
    cache_clear()


def ingest_environment(db: Session, payload: dict) -> None:
    dept = department_by_code(db, payload["department"])
    device, _ = _touch_device(db, payload["device_id"], payload.get("temperature"))
    if not dept or not device:
        raise ValueError("Unknown department or device")
    db.add(
        EnvironmentReading(
            device_id=device.id,
            department_id=dept.id,
            timestamp=payload.get("timestamp") or utcnow(),
            temperature=payload["temperature"],
            humidity=payload["humidity"],
            occupancy=payload["occupancy"],
            is_simulated=payload.get("is_simulated", True),
        )
    )
    db.commit()


def ingest_heartbeat(db: Session, payload: dict) -> None:
    _touch_device(db, payload["device_id"], payload.get("last_value"))
    db.commit()
