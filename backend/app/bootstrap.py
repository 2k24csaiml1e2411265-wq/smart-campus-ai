from datetime import timedelta
from pathlib import Path

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import SessionLocal
from app.dependencies import hash_password
from app.ml.anomaly_detection import evaluate_with_labels, train_isolation_forest
from app.ml.feature_engineering import FEATURE_COLUMNS, feature_matrix, readings_to_frame
from app.ml.forecasting import train_forecast
from app.ml.model_manager import manager
from app.models.department import Department
from app.models.device import Device, DeviceStatus, DeviceType
from app.models.readings import EnergyReading, EnvironmentReading, SolarReading, WaterReading
from app.models.user import User, UserRole
from app.utils.campus import DEPARTMENTS, devices_for
from app.utils.logging import logger
from app.utils.time import utcnow

settings = get_settings()


def _ensure_catalog(db: Session) -> None:
    if db.scalar(select(func.count(Department.id))) == 0:
        for spec in DEPARTMENTS:
            db.add(
                Department(
                    name=spec["name"],
                    code=spec["code"],
                    building=spec["building"],
                    floor_area=spec["floor_area"],
                    student_count=spec["student_count"],
                    staff_count=spec["staff_count"],
                    active=True,
                )
            )
        db.commit()
    depts = {d.code: d for d in db.scalars(select(Department)).all()}
    if db.scalar(select(func.count(Device.id))) == 0:
        for code, dept in depts.items():
            for spec in devices_for(code):
                db.add(
                    Device(
                        device_id=spec["device_id"],
                        department_id=dept.id,
                        device_type=DeviceType(spec["device_type"]),
                        location=spec["location"],
                        status=DeviceStatus.online,
                        last_seen=utcnow(),
                    )
                )
        db.commit()
    if db.scalar(select(func.count(User.id))) == 0:
        cse = depts["CSE"]
        users = [
            ("admin@psit.ac.in", "admin123", UserRole.admin, None, "Campus Admin"),
            ("facility@psit.ac.in", "facility123", UserRole.facility_manager, None, "Facility Manager"),
            ("cse.manager@psit.ac.in", "manager123", UserRole.department_manager, cse.id, "CSE Manager"),
            ("viewer@psit.ac.in", "viewer123", UserRole.viewer, None, "Viewer"),
        ]
        for email, pw, role, dept_id, name in users:
            db.add(
                User(
                    email=email,
                    password_hash=hash_password(pw),
                    role=role,
                    department_id=dept_id,
                    full_name=name,
                )
            )
        db.commit()


def seed_history(db: Session, days: int = 7, step_hours: int = 1) -> int:
    if db.scalar(select(func.count(EnergyReading.id))) > 100:
        return 0
    import sys

    sys.path.append(str(Path(__file__).resolve().parents[2] / "simulator"))
    from engine import generate_tick

    depts = {d.code: d for d in db.scalars(select(Department)).all()}
    devices = {(d.device_id): d for d in db.scalars(select(Device)).all()}
    start = utcnow() - timedelta(days=days)
    count = 0
    steps = days * 24 // step_hours
    for i in range(steps):
        ts = start + timedelta(hours=i * step_hours)
        weather = 0.75 + 0.25 * ((i % 24) / 24)
        for spec in DEPARTMENTS:
            dept = depts[spec["code"]]
            injected = i % 37 == 0 and spec["code"] == "ME"
            tick = generate_tick(spec, ts, anomaly=injected, weather=weather)
            e1 = devices[f"{spec['code']}-F1-ENERGY-01"]
            e2 = devices[f"{spec['code']}-F2-ENERGY-02"]
            s1 = devices[f"{spec['code']}-SOLAR-01"]
            w1 = devices[f"{spec['code']}-WATER-01"]
            n1 = devices[f"{spec['code']}-ENV-01"]
            e = tick["energy"]
            db.add(
                EnergyReading(
                    device_id=e1.id,
                    department_id=dept.id,
                    timestamp=ts,
                    energy_kwh=e["energy_kwh"] * 0.55,
                    voltage=e["voltage"],
                    current=e["current"] * 0.55,
                    power_factor=e["power_factor"],
                    temperature=e["temperature"],
                    occupancy=e["occupancy"],
                    is_simulated=True,
                    is_anomaly_injected=injected,
                )
            )
            db.add(
                EnergyReading(
                    device_id=e2.id,
                    department_id=dept.id,
                    timestamp=ts,
                    energy_kwh=e["energy_kwh"] * 0.45,
                    voltage=e["voltage"],
                    current=e["current"] * 0.45,
                    power_factor=e["power_factor"],
                    temperature=e["temperature"],
                    occupancy=int(e["occupancy"] * 0.8),
                    is_simulated=True,
                    is_anomaly_injected=injected,
                )
            )
            sol = tick["solar"]
            db.add(
                SolarReading(
                    device_id=s1.id,
                    department_id=dept.id,
                    timestamp=ts,
                    solar_kwh=sol["solar_kwh"],
                    voltage=sol["voltage"],
                    current=sol["current"],
                    irradiance=sol["irradiance"],
                    is_simulated=True,
                )
            )
            wat = tick["water"]
            db.add(
                WaterReading(
                    device_id=w1.id,
                    department_id=dept.id,
                    timestamp=ts,
                    water_litres=wat["water_litres"],
                    flow_rate=wat["flow_rate"],
                    pressure=wat["pressure"],
                    is_simulated=True,
                    is_anomaly_injected=injected,
                )
            )
            env = tick["environment"]
            db.add(
                EnvironmentReading(
                    device_id=n1.id,
                    department_id=dept.id,
                    timestamp=ts,
                    temperature=env["temperature"],
                    humidity=env["humidity"],
                    occupancy=env["occupancy"],
                    is_simulated=True,
                )
            )
            count += 5
        if i % 24 == 0:
            db.commit()
    db.commit()
    logger.info("seed_history_complete", rows=count, days=days)
    return count


def train_from_database(db: Session) -> dict:
    rows = db.scalars(
        select(EnergyReading)
        .order_by(EnergyReading.timestamp.asc())
        .limit(20000)
    ).all()

    payload = [
        {
            "timestamp": r.timestamp,
            "energy_kwh": r.energy_kwh,
            "occupancy": r.occupancy,
            "temperature": r.temperature,
            "solar_generation": 0.0,
            "label": int(r.is_anomaly_injected),
        }
        for r in rows
    ]

    if len(payload) < 48:
        return {"trained": False, "reason": "insufficient history"}

    train_isolation_forest(payload)
    train_forecast(payload)

    df = readings_to_frame(payload)
    X = feature_matrix(df, FEATURE_COLUMNS)

    labels = [int(p["label"]) for p in payload]

    import pandas as pd

    dfl = pd.DataFrame(payload)
    dfl["timestamp"] = pd.to_datetime(dfl["timestamp"], utc=True)

    # Keep the training labels separate from any existing
    # "label" column in df to prevent label_x / label_y collisions.
    labels_df = dfl[["timestamp", "label"]].rename(
        columns={"label": "__target_label"}
    )

    merged = df.merge(
        labels_df,
        on="timestamp",
        how="left",
    )

    y = merged["__target_label"].fillna(0).astype(int).to_numpy()

    metrics = evaluate_with_labels(X, y)

    existing = manager.metrics or {}
    existing["anomaly"] = metrics

    manager.save_metrics(existing)

    logger.info(
        "ml_trained",
        anomaly=metrics,
        forecast=existing.get("forecast"),
    )

    return {
        "trained": True,
        "anomaly": metrics,
        "forecast": existing.get("forecast"),
    }


def bootstrap() -> None:
    Path("data").mkdir(exist_ok=True)
    db = SessionLocal()
    try:
        _ensure_catalog(db)
        seed_history(db, days=8)
        if not manager.ready:
            train_from_database(db)
    finally:
        db.close()
