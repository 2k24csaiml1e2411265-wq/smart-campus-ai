import csv
import io

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import Response, StreamingResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user, require_roles
from app.models.anomaly import Anomaly
from app.models.department import Department
from app.models.device import Device, DeviceType
from app.models.user import User, UserRole
from app.schemas import DepartmentUpdate
from app.services.analytics import compute_scores, summary_for_period
from app.services.ingestion import ingest_energy
from app.services.lookups import department_by_code, require_department
from app.services.realtime import mark_simulator
from app.services.reports import build_sustainability_pdf
from app.utils.time import utcnow

router = APIRouter(tags=["admin-reports"])


@router.patch("/admin/departments/{department}")
def update_department(
    department: str,
    body: DepartmentUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(UserRole.admin, UserRole.facility_manager)),
):
    dept = require_department(db, department)
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(dept, field, value)
    db.commit()
    return {"ok": True, "code": dept.code}


@router.get("/admin/health-extended")
def admin_health(
    user: User = Depends(require_roles(UserRole.admin)),
    db: Session = Depends(get_db),
):
    from app.routes.health import health

    return health(db)


@router.post("/simulator/anomaly")
def trigger_anomaly(
    department: str = "ME",
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(UserRole.admin, UserRole.facility_manager)),
):
    dept = department_by_code(db, department)
    if not dept:
        raise HTTPException(status_code=404, detail="Unknown department")
    device = (
        db.query(Device)
        .filter(Device.department_id == dept.id, Device.device_type == DeviceType.energy_meter)
        .first()
    )
    if not device:
        raise HTTPException(status_code=404, detail="No energy meter")
    event = ingest_energy(
        db,
        {
            "device_id": device.device_id,
            "department": dept.code,
            "energy_kwh": 96.4,
            "voltage": 228.0,
            "current": 42.0,
            "power_factor": 0.78,
            "temperature": 37.5,
            "occupancy": 95,
            "is_simulated": True,
            "is_anomaly_injected": True,
        },
    )
    mark_simulator("running")
    return {"ok": True, "event": event}


@router.post("/ml/retrain")
def retrain(
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(UserRole.admin)),
):
    from app.bootstrap import train_from_database

    result = train_from_database(db)
    return {"ok": True, **result}


def _report_payload(db: Session, period: str, department: str | None) -> dict:
    dept_id = require_department(db, department).id if department else None
    summary = summary_for_period(db, period, dept_id)
    scores = compute_scores(db, period)
    anomalies = db.execute(
        select(Anomaly, Department.code).join(Department, Department.id == Anomaly.department_id).order_by(Anomaly.timestamp.desc()).limit(20)
    ).all()
    anomaly_list = [
        {
            "department_code": code,
            "severity": a.severity.value,
            "reason": a.reason,
            "recommendation": a.recommendation,
        }
        for a, code in anomalies
    ]
    return {
        **summary,
        "generated_at": utcnow().isoformat(),
        "scores": scores,
        "anomaly_list": anomaly_list,
        "forecast_list": [],
        "recommendations": [{"title": a["reason"][:80], "recommendation": a["recommendation"]} for a in anomaly_list],
    }


@router.post("/reports/generate")
def generate_report(
    period: str = Query("7d"),
    fmt: str = Query("pdf"),
    department: str | None = None,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(UserRole.admin, UserRole.facility_manager, UserRole.department_manager)),
):
    payload = _report_payload(db, period, department)
    if fmt == "json":
        return payload
    if fmt == "csv":
        buf = io.StringIO()
        writer = csv.writer(buf)
        writer.writerow(["metric", "value"])
        for k, v in payload.items():
            if k in {"scores", "anomaly_list", "forecast_list", "recommendations"}:
                continue
            writer.writerow([k, v])
        writer.writerow([])
        writer.writerow(["code", "total_score", "kwh_per_student", "kwh_per_sqm"])
        for s in payload["scores"]:
            writer.writerow([s["code"], s["total_score"], s["kwh_per_student"], s["kwh_per_sqm"]])
        return StreamingResponse(
            iter([buf.getvalue()]),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=campus-{period}.csv"},
        )
    pdf = build_sustainability_pdf(payload)
    return Response(
        content=pdf,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=smart-campus-{period}.pdf"},
    )


@router.get("/export")
def export_data(
    period: str = Query("7d"),
    department: str | None = None,
    fmt: str = Query("csv"),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    if user.role == UserRole.viewer:
        raise HTTPException(status_code=403, detail="Viewers cannot export detailed reports")
    return generate_report(period=period, fmt=fmt, department=department, db=db, user=user)
