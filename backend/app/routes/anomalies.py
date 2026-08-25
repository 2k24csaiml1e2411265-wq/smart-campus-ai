from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user, require_roles
from app.models.anomaly import Anomaly, AnomalyStatus
from app.models.department import Department
from app.models.user import User, UserRole
from app.schemas import AnomalyStatusUpdate

router = APIRouter(tags=["anomalies"])


@router.get("/anomalies")
def list_anomalies(
    status: str | None = None,
    department: str | None = None,
    severity: str | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    stmt = select(Anomaly, Department.code).join(Department, Department.id == Anomaly.department_id)
    if status:
        stmt = stmt.where(Anomaly.status == AnomalyStatus(status))
    if severity:
        stmt = stmt.where(Anomaly.severity == severity)
    if department:
        stmt = stmt.where(Department.code == department.upper())
    stmt = stmt.order_by(Anomaly.timestamp.desc())
    rows = db.execute(stmt.offset((page - 1) * page_size).limit(page_size)).all()
    return [
        {
            "id": a.id,
            "department_code": code,
            "timestamp": a.timestamp.isoformat(),
            "metric": a.metric,
            "actual_value": a.actual_value,
            "expected_value": a.expected_value,
            "deviation_pct": round(((a.actual_value - a.expected_value) / a.expected_value * 100) if a.expected_value else 0, 1),
            "anomaly_score": a.anomaly_score,
            "severity": a.severity.value,
            "reason": a.reason,
            "recommendation": a.recommendation,
            "status": a.status.value,
        }
        for a, code in rows
    ]


@router.patch("/anomalies/{anomaly_id}")
def update_anomaly(
    anomaly_id: int,
    body: AnomalyStatusUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(UserRole.admin, UserRole.facility_manager, UserRole.department_manager)),
):
    a = db.get(Anomaly, anomaly_id)
    if not a:
        raise HTTPException(status_code=404, detail="Anomaly not found")
    if body.status not in {"open", "acknowledged", "resolved"}:
        raise HTTPException(status_code=400, detail="Invalid status")
    a.status = AnomalyStatus(body.status)
    db.commit()
    return {"ok": True, "id": a.id, "status": a.status.value}


@router.get("/recommendations")
def recommendations(db: Session = Depends(get_db)):
    rows = db.execute(
        select(Anomaly, Department.code)
        .join(Department, Department.id == Anomaly.department_id)
        .where(Anomaly.status != AnomalyStatus.resolved)
        .order_by(Anomaly.timestamp.desc())
        .limit(20)
    ).all()
    recs = []
    for a, code in rows:
        recs.append(
            {
                "type": "ANOMALY",
                "department": code,
                "title": f"{code} {a.metric} is {abs((a.actual_value - a.expected_value) / (a.expected_value or 1) * 100):.0f}% from expected.",
                "recommendation": a.recommendation,
                "severity": a.severity.value,
                "evidence": [a.reason.split("\n")[0]],
            }
        )
    return recs
