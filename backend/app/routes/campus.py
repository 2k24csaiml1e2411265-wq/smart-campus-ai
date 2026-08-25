from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_db
from app.dependencies import get_current_user, get_optional_user, scoped_department_id
from app.models.anomaly import Anomaly, AnomalyStatus
from app.models.department import Department
from app.models.device import Device
from app.models.readings import EnergyReading, SolarReading, WaterReading
from app.models.user import User
from app.services.analytics import compute_scores, department_energy_totals, hourly_campus_energy, summary_for_period
from app.services.lookups import last_energy_timestamp, require_department
from app.services.realtime import cache_get, cache_set
from app.utils.time import period_start, utcnow

router = APIRouter(tags=["campus"])
settings = get_settings()


@router.get("/dashboard")
def dashboard(
    period: str = Query("24h"),
    db: Session = Depends(get_db),
    user: User | None = Depends(get_optional_user),
):
    cached = cache_get(f"dashboard:{period}:{user.id if user else 'anon'}")
    if cached:
        return cached
    dept_id = None
    if user:
        dept_id = scoped_department_id(user, None)
    summary = summary_for_period(db, period, dept_id)
    start = period_start(period)
    end = utcnow()
    by_dept = department_energy_totals(db, start, end)
    trend = hourly_campus_energy(db, start, end)
    score_period = "24h" if period in {"24h", "today"} else period if period in {"7d", "30d"} else "7d"
    scores = compute_scores(db, score_period)
    anomalies = (
        db.execute(
            select(Anomaly, Department.code)
            .join(Department, Department.id == Anomaly.department_id)
            .where(Anomaly.status != AnomalyStatus.resolved)
            .order_by(Anomaly.timestamp.desc())
            .limit(8)
        ).all()
    )
    solar_trend = db.execute(
        select(func.strftime("%Y-%m-%dT%H:00:00", SolarReading.timestamp), func.sum(SolarReading.solar_kwh))
        .where(SolarReading.timestamp >= start, SolarReading.timestamp <= end)
        .group_by(func.strftime("%Y-%m-%dT%H:00:00", SolarReading.timestamp))
        .order_by(func.strftime("%Y-%m-%dT%H:00:00", SolarReading.timestamp))
    ).all()
    water_trend = db.execute(
        select(func.strftime("%Y-%m-%dT%H:00:00", WaterReading.timestamp), func.sum(WaterReading.water_litres))
        .where(WaterReading.timestamp >= start, WaterReading.timestamp <= end)
        .group_by(func.strftime("%Y-%m-%dT%H:00:00", WaterReading.timestamp))
        .order_by(func.strftime("%Y-%m-%dT%H:00:00", WaterReading.timestamp))
    ).all()
    payload = {
        "campus": settings.campus_name,
        "data_mode": settings.data_mode,
        "last_updated": (last_energy_timestamp(db) or utcnow()).isoformat(),
        "summary": summary,
        "energy_by_department": by_dept,
        "energy_trend": trend,
        "solar_trend": [{"timestamp": str(r[0]), "solar_kwh": round(float(r[1] or 0), 2)} for r in solar_trend],
        "water_trend": [{"timestamp": str(r[0]), "water_litres": round(float(r[1] or 0), 2)} for r in water_trend],
        "scores": scores,
        "alerts": [
            {
                "id": a.id,
                "department_code": code,
                "severity": a.severity.value,
                "metric": a.metric,
                "actual_value": a.actual_value,
                "expected_value": a.expected_value,
                "reason": a.reason,
                "recommendation": a.recommendation,
                "status": a.status.value,
                "timestamp": a.timestamp.isoformat(),
            }
            for a, code in anomalies
        ],
        "recommendations": [
            {
                "type": "ANOMALY",
                "department": code,
                "title": f"{code} {a.metric} anomaly ({a.severity.value})",
                "recommendation": a.recommendation,
                "severity": a.severity.value,
            }
            for a, code in anomalies[:5]
        ],
    }
    cache_set(f"dashboard:{period}:{user.id if user else 'anon'}", payload)
    return payload


@router.get("/summary")
def summary(
    period: str = Query("24h"),
    department: str | None = None,
    db: Session = Depends(get_db),
    user: User | None = Depends(get_optional_user),
):
    if period not in {"24h", "7d", "30d", "today"}:
        raise HTTPException(status_code=400, detail="Invalid period. Use 24h, 7d, or 30d.")
    dept_id = None
    if department:
        dept_id = require_department(db, department).id
    if user:
        scoped = scoped_department_id(user, dept_id)
        dept_id = scoped
    return summary_for_period(db, "24h" if period == "today" else period, dept_id)


@router.get("/departments")
def departments(db: Session = Depends(get_db)):
    rows = db.scalars(select(Department).order_by(Department.code)).all()
    return [
        {
            "id": d.id,
            "name": d.name,
            "code": d.code,
            "building": d.building,
            "floor_area": d.floor_area,
            "student_count": d.student_count,
            "staff_count": d.staff_count,
            "active": d.active,
        }
        for d in rows
    ]


@router.get("/departments/{department}")
def department_detail(department: str, period: str = "7d", db: Session = Depends(get_db)):
    dept = require_department(db, department)
    summary = summary_for_period(db, period, dept.id)
    scores = [s for s in compute_scores(db, period) if s["code"] == dept.code]
    return {"department": {"id": dept.id, "code": dept.code, "name": dept.name, "building": dept.building, "floor_area": dept.floor_area, "student_count": dept.student_count, "staff_count": dept.staff_count}, "summary": summary, "score": scores[0] if scores else None}


@router.get("/scores")
def scores(period: str = "7d", db: Session = Depends(get_db)):
    return compute_scores(db, period)


@router.get("/energy/latest")
def energy_latest(db: Session = Depends(get_db)):
    sub = (
        select(EnergyReading.department_id, func.max(EnergyReading.timestamp).label("ts"))
        .group_by(EnergyReading.department_id)
        .subquery()
    )
    rows = db.execute(
        select(EnergyReading, Department.code)
        .join(Department, Department.id == EnergyReading.department_id)
        .join(sub, (EnergyReading.department_id == sub.c.department_id) & (EnergyReading.timestamp == sub.c.ts))
    ).all()
    return [
        {
            "department": code,
            "timestamp": r.timestamp.isoformat(),
            "energy_kwh": r.energy_kwh,
            "voltage": r.voltage,
            "current": r.current,
            "power_factor": r.power_factor,
            "temperature": r.temperature,
            "occupancy": r.occupancy,
            "is_simulated": r.is_simulated,
        }
        for r, code in rows
    ]


@router.get("/energy/trend/{department}")
def energy_trend(department: str, period: str = "24h", db: Session = Depends(get_db)):
    dept = require_department(db, department)
    start = period_start(period)
    hour_expr = func.strftime("%Y-%m-%dT%H:00:00", EnergyReading.timestamp)
    rows = db.execute(
        select(hour_expr, func.sum(EnergyReading.energy_kwh))
        .where(EnergyReading.department_id == dept.id, EnergyReading.timestamp >= start)
        .group_by(hour_expr)
        .order_by(hour_expr)
    ).all()
    return [{"timestamp": str(r[0]), "energy_kwh": round(float(r[1] or 0), 2)} for r in rows]


@router.get("/energy/history/{department}")
def energy_history(
    department: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db),
):
    dept = require_department(db, department)
    q = select(EnergyReading).where(EnergyReading.department_id == dept.id).order_by(EnergyReading.timestamp.desc())
    total = db.scalar(select(func.count()).select_from(q.subquery()))
    rows = db.scalars(q.offset((page - 1) * page_size).limit(page_size)).all()
    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": [
            {
                "timestamp": r.timestamp.isoformat(),
                "energy_kwh": r.energy_kwh,
                "temperature": r.temperature,
                "occupancy": r.occupancy,
                "is_simulated": r.is_simulated,
            }
            for r in rows
        ],
    }


@router.get("/solar/latest")
def solar_latest(db: Session = Depends(get_db)):
    sub = select(SolarReading.department_id, func.max(SolarReading.timestamp).label("ts")).group_by(SolarReading.department_id).subquery()
    rows = db.execute(
        select(SolarReading, Department.code)
        .join(Department, Department.id == SolarReading.department_id)
        .join(sub, (SolarReading.department_id == sub.c.department_id) & (SolarReading.timestamp == sub.c.ts))
    ).all()
    return [
        {
            "department": code,
            "timestamp": r.timestamp.isoformat(),
            "solar_kwh": r.solar_kwh,
            "irradiance": r.irradiance,
            "is_simulated": r.is_simulated,
        }
        for r, code in rows
    ]


@router.get("/water/latest")
def water_latest(db: Session = Depends(get_db)):
    sub = select(WaterReading.department_id, func.max(WaterReading.timestamp).label("ts")).group_by(WaterReading.department_id).subquery()
    rows = db.execute(
        select(WaterReading, Department.code)
        .join(Department, Department.id == WaterReading.department_id)
        .join(sub, (WaterReading.department_id == sub.c.department_id) & (WaterReading.timestamp == sub.c.ts))
    ).all()
    return [
        {
            "department": code,
            "timestamp": r.timestamp.isoformat(),
            "water_litres": r.water_litres,
            "flow_rate": r.flow_rate,
            "pressure": r.pressure,
            "is_simulated": r.is_simulated,
        }
        for r, code in rows
    ]
