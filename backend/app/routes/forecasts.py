from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.database import get_db
from app.ml.forecasting import forecast_department
from app.models.department import Department
from app.models.forecast import Forecast
from app.models.readings import EnergyReading, SolarReading
from app.services.lookups import require_department
from app.utils.time import utcnow

router = APIRouter(tags=["forecasts"])


@router.get("/forecasts")
def forecasts(department: str | None = None, db: Session = Depends(get_db)):
    stmt = select(Forecast, Department.code).join(Department, Department.id == Forecast.department_id)
    if department:
        stmt = stmt.where(Department.code == department.upper())
    stmt = stmt.order_by(Forecast.forecast_for.asc())
    rows = db.execute(stmt.limit(200)).all()
    if rows:
        return [
            {
                "department_code": code,
                "timestamp": f.timestamp.isoformat(),
                "forecast_for": f.forecast_for.isoformat(),
                "predicted_kwh": f.predicted_kwh,
                "lower_bound": f.lower_bound,
                "upper_bound": f.upper_bound,
                "model_name": f.model_name,
                "horizon_hours": f.horizon_hours,
                "confidence": f.confidence,
            }
            for f, code in rows
        ]
    depts = [require_department(db, department)] if department else db.scalars(select(Department)).all()
    out = []
    for d in depts:
        out.extend(_build_and_store(db, d))
    return out


def _build_and_store(db: Session, dept: Department) -> list[dict]:
    hist = db.scalars(
        select(EnergyReading)
        .where(EnergyReading.department_id == dept.id)
        .order_by(EnergyReading.timestamp.desc())
        .limit(200)
    ).all()
    solar = {
        r.timestamp.replace(minute=0, second=0, microsecond=0): r.solar_kwh
        for r in db.scalars(
            select(SolarReading).where(SolarReading.department_id == dept.id).order_by(SolarReading.timestamp.desc()).limit(200)
        ).all()
    }
    history = [
        {
            "timestamp": r.timestamp,
            "energy_kwh": r.energy_kwh,
            "occupancy": r.occupancy,
            "temperature": r.temperature,
            "solar_generation": solar.get(r.timestamp.replace(minute=0, second=0, microsecond=0), 0),
        }
        for r in reversed(list(hist))
    ]
    preds = forecast_department(dept.code, history)
    db.execute(delete(Forecast).where(Forecast.department_id == dept.id))
    for p in preds:
        db.add(
            Forecast(
                department_id=dept.id,
                timestamp=p["timestamp"],
                forecast_for=p["forecast_for"],
                predicted_kwh=p["predicted_kwh"],
                lower_bound=p["lower_bound"],
                upper_bound=p["upper_bound"],
                model_name=p["model_name"],
                horizon_hours=p["horizon_hours"],
                confidence=p["confidence"],
            )
        )
    db.commit()
    latest = hist[0] if hist else None
    peak = max(preds, key=lambda x: x["predicted_kwh"]) if preds else None
    low = min(preds, key=lambda x: x["predicted_kwh"]) if preds else None
    meta = {
        "current_kwh": latest.energy_kwh if latest else None,
        "expected_peak": peak["forecast_for"].isoformat() if peak else None,
        "expected_low": low["forecast_for"].isoformat() if low else None,
        "next_hour": preds[0]["predicted_kwh"] if preds else None,
    }
    return [{**p, "timestamp": p["timestamp"].isoformat(), "forecast_for": p["forecast_for"].isoformat(), **({"meta": meta} if i == 0 else {})} for i, p in enumerate(preds)]
