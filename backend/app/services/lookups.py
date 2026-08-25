from datetime import datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.department import Department
from app.models.device import Device, DeviceStatus
from app.models.readings import EnergyReading
from app.utils.time import utcnow


def department_by_code(db: Session, code: str) -> Department | None:
    return db.scalar(select(Department).where(func.lower(Department.code) == code.lower()))


def require_department(db: Session, code: str) -> Department:
    dept = department_by_code(db, code)
    if not dept:
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail=f"Unknown department: {code}")
    return dept


def device_by_external_id(db: Session, device_id: str) -> Device | None:
    return db.scalar(select(Device).where(Device.device_id == device_id))


def last_energy_timestamp(db: Session) -> datetime | None:
    return db.scalar(select(func.max(EnergyReading.timestamp)))


def refresh_device_heartbeats(db: Session) -> None:
    cutoff = utcnow() - timedelta(minutes=3)
    warning_cut = utcnow() - timedelta(minutes=1)
    devices = db.scalars(select(Device)).all()
    for d in devices:
        if d.last_seen is None or d.last_seen < cutoff:
            d.status = DeviceStatus.offline
        elif d.last_seen < warning_cut:
            d.status = DeviceStatus.warning
        else:
            d.status = DeviceStatus.online
    db.commit()
