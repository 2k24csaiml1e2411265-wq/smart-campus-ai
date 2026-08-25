from sqlalchemy import case, func, select
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models.anomaly import Anomaly, AnomalyStatus
from app.models.department import Department
from app.models.readings import EnergyReading, SolarReading, WaterReading
from app.services.green_score import score_department
from app.utils.time import period_start, utcnow

settings = get_settings()


def summary_for_period(db: Session, period: str, department_id: int | None = None) -> dict:
    end = utcnow()
    start = period_start(period, end)
    prior_start = start - (end - start)

    energy_q = select(
        func.coalesce(func.sum(EnergyReading.energy_kwh), 0),
        func.coalesce(func.avg(EnergyReading.energy_kwh), 0),
        func.coalesce(func.max(EnergyReading.energy_kwh), 0),
        func.count(EnergyReading.id),
    ).where(EnergyReading.timestamp >= start, EnergyReading.timestamp <= end)
    solar_q = select(func.coalesce(func.sum(SolarReading.solar_kwh), 0)).where(
        SolarReading.timestamp >= start, SolarReading.timestamp <= end
    )
    water_q = select(func.coalesce(func.sum(WaterReading.water_litres), 0)).where(
        WaterReading.timestamp >= start, WaterReading.timestamp <= end
    )
    anomaly_q = select(func.count(Anomaly.id)).where(Anomaly.timestamp >= start, Anomaly.timestamp <= end)
    if department_id:
        energy_q = energy_q.where(EnergyReading.department_id == department_id)
        solar_q = solar_q.where(SolarReading.department_id == department_id)
        water_q = water_q.where(WaterReading.department_id == department_id)
        anomaly_q = anomaly_q.where(Anomaly.department_id == department_id)

    total_energy, avg_energy, peak_energy, n_energy = db.execute(energy_q).one()
    total_solar = db.execute(solar_q).scalar_one()
    total_water = db.execute(water_q).scalar_one()
    n_anomalies = db.execute(anomaly_q).scalar_one()

    solar_share = float(total_solar) / float(total_energy) if total_energy else 0.0
    co2_avoided = float(total_solar) * settings.co2_kg_per_kwh

    return {
        "period": period,
        "start": start.isoformat(),
        "end": end.isoformat(),
        "total_energy_kwh": round(float(total_energy), 2),
        "total_solar_kwh": round(float(total_solar), 2),
        "total_water_litres": round(float(total_water), 2),
        "solar_share": round(solar_share, 4),
        "co2_avoided_kg": round(co2_avoided, 2),
        "average_consumption_kwh": round(float(avg_energy), 2),
        "peak_consumption_kwh": round(float(peak_energy), 2),
        "sample_count": int(n_energy),
        "anomalies": int(n_anomalies),
        "co2_factor_kg_per_kwh": settings.co2_kg_per_kwh,
        "co2_factor_source": settings.co2_factor_source,
        "data_mode": settings.data_mode,
        "campus": settings.campus_name,
        "prior_window_start": prior_start.isoformat(),
    }


def department_energy_totals(db: Session, start, end) -> list[dict]:
    stmt = (
        select(
            Department.code,
            Department.name,
            func.coalesce(func.sum(EnergyReading.energy_kwh), 0).label("energy_kwh"),
        )
        .join(EnergyReading, EnergyReading.department_id == Department.id, isouter=True)
        .where((EnergyReading.timestamp >= start) | (EnergyReading.id.is_(None)))
        .where((EnergyReading.timestamp <= end) | (EnergyReading.id.is_(None)))
        .group_by(Department.id)
        .order_by(Department.code)
    )
    # Simpler, correct aggregation without outer-join timestamp pitfalls:
    depts = db.scalars(select(Department).where(Department.active.is_(True)).order_by(Department.code)).all()
    energy_rows = db.execute(
        select(EnergyReading.department_id, func.sum(EnergyReading.energy_kwh))
        .where(EnergyReading.timestamp >= start, EnergyReading.timestamp <= end)
        .group_by(EnergyReading.department_id)
    ).all()
    solar_rows = db.execute(
        select(SolarReading.department_id, func.sum(SolarReading.solar_kwh))
        .where(SolarReading.timestamp >= start, SolarReading.timestamp <= end)
        .group_by(SolarReading.department_id)
    ).all()
    water_rows = db.execute(
        select(WaterReading.department_id, func.sum(WaterReading.water_litres))
        .where(WaterReading.timestamp >= start, WaterReading.timestamp <= end)
        .group_by(WaterReading.department_id)
    ).all()
    energy_map = {r[0]: float(r[1] or 0) for r in energy_rows}
    solar_map = {r[0]: float(r[1] or 0) for r in solar_rows}
    water_map = {r[0]: float(r[1] or 0) for r in water_rows}
    return [
        {
            "id": d.id,
            "code": d.code,
            "name": d.name,
            "energy_kwh": round(energy_map.get(d.id, 0.0), 2),
            "solar_kwh": round(solar_map.get(d.id, 0.0), 2),
            "water_litres": round(water_map.get(d.id, 0.0), 2),
        }
        for d in depts
    ]


def hourly_campus_energy(db: Session, start, end) -> list[dict]:
    hour_expr = func.strftime("%Y-%m-%dT%H:00:00", EnergyReading.timestamp)
    if db.get_bind().dialect.name == "postgresql":
        hour_expr = func.date_trunc("hour", EnergyReading.timestamp)
    stmt = (
        select(hour_expr.label("bucket"), func.sum(EnergyReading.energy_kwh), func.sum(SolarReading.solar_kwh))
        if False
        else select(hour_expr.label("bucket"), func.sum(EnergyReading.energy_kwh).label("energy"))
        .where(EnergyReading.timestamp >= start, EnergyReading.timestamp <= end)
        .group_by("bucket")
        .order_by("bucket")
    )
    rows = db.execute(stmt).all()
    return [{"timestamp": str(r[0]), "energy_kwh": round(float(r[1] or 0), 2)} for r in rows]


def compute_scores(db: Session, period: str = "7d") -> list[dict]:
    end = utcnow()
    start = period_start(period, end)
    prior_start = start - (end - start)
    depts = db.scalars(select(Department).where(Department.active.is_(True))).all()
    energy = dict(
        db.execute(
            select(EnergyReading.department_id, func.sum(EnergyReading.energy_kwh))
            .where(EnergyReading.timestamp >= start, EnergyReading.timestamp <= end)
            .group_by(EnergyReading.department_id)
        ).all()
    )
    prior = dict(
        db.execute(
            select(EnergyReading.department_id, func.sum(EnergyReading.energy_kwh))
            .where(EnergyReading.timestamp >= prior_start, EnergyReading.timestamp < start)
            .group_by(EnergyReading.department_id)
        ).all()
    )
    solar = dict(
        db.execute(
            select(SolarReading.department_id, func.sum(SolarReading.solar_kwh))
            .where(SolarReading.timestamp >= start, SolarReading.timestamp <= end)
            .group_by(SolarReading.department_id)
        ).all()
    )
    water = dict(
        db.execute(
            select(WaterReading.department_id, func.sum(WaterReading.water_litres))
            .where(WaterReading.timestamp >= start, WaterReading.timestamp <= end)
            .group_by(WaterReading.department_id)
        ).all()
    )
    anomalies = dict(
        db.execute(
            select(Anomaly.department_id, func.count(Anomaly.id))
            .where(Anomaly.timestamp >= start, Anomaly.timestamp <= end)
            .group_by(Anomaly.department_id)
        ).all()
    )
    stats = db.execute(
        select(
            EnergyReading.department_id,
            func.avg(EnergyReading.energy_kwh),
            func.count(EnergyReading.id),
        )
        .where(EnergyReading.timestamp >= start, EnergyReading.timestamp <= end)
        .group_by(EnergyReading.department_id)
    ).all()
    stat_map = {r[0]: (float(r[1] or 0), float((r[1] or 0) * 0.18), int(r[2] or 0)) for r in stats}

    out = []
    for d in depts:
        mean, std, n = stat_map.get(d.id, (0.0, 0.0, 0))
        payload = score_department(
            kwh=float(energy.get(d.id, 0) or 0),
            students=d.student_count,
            area=d.floor_area,
            prior_kwh=float(prior.get(d.id, 0) or 0),
            solar_kwh=float(solar.get(d.id, 0) or 0),
            water_litres=float(water.get(d.id, 0) or 0),
            anomaly_count=int(anomalies.get(d.id, 0) or 0),
            hours=max(n, 1),
            energy_series_std=std,
            energy_series_mean=mean or 1,
        )
        out.append({"department_id": d.id, "code": d.code, "name": d.name, **payload})
    out.sort(key=lambda x: x["total_score"], reverse=True)
    return out
