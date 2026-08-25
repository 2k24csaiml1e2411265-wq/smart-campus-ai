from datetime import timedelta

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.department import Department
from app.models.device import Device, DeviceStatus
from app.services.lookups import refresh_device_heartbeats
from app.utils.time import utcnow

router = APIRouter(tags=["devices"])


@router.get("/devices")
def devices(db: Session = Depends(get_db)):
    refresh_device_heartbeats(db)
    rows = db.execute(select(Device, Department.code).join(Department, Department.id == Device.department_id).order_by(Device.device_id)).all()
    now = utcnow()
    out = []
    for d, code in rows:
        age = (now - d.last_seen).total_seconds() if d.last_seen else None
        health = "healthy"
        if d.status == DeviceStatus.offline:
            health = "offline"
        elif d.status == DeviceStatus.warning:
            health = "degraded"
        out.append(
            {
                "id": d.id,
                "device_id": d.device_id,
                "department_code": code,
                "device_type": d.device_type.value,
                "location": d.location,
                "status": d.status.value.upper(),
                "last_seen": d.last_seen.isoformat() if d.last_seen else None,
                "last_value": d.last_value,
                "health": health,
                "heartbeat_age_seconds": age,
            }
        )
    return out


@router.get("/devices/status")
def device_status(db: Session = Depends(get_db)):
    rows = devices(db)
    counts = {"ONLINE": 0, "OFFLINE": 0, "WARNING": 0}
    for r in rows:
        counts[r["status"]] = counts.get(r["status"], 0) + 1
    return {"counts": counts, "devices": rows}
