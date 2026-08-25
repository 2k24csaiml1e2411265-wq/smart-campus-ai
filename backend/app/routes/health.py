from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, text
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_db
from app.ml.model_manager import manager
from app.models.readings import EnergyReading
from app.schemas import HealthOut
from app.services.lookups import last_energy_timestamp
from app.services.realtime import runtime_state, ws_manager

router = APIRouter(tags=["health"])
settings = get_settings()


@router.get("/health", response_model=HealthOut)
def health(db: Session = Depends(get_db)):
    db_status = "healthy"
    try:
        db.execute(text("SELECT 1"))
    except Exception:
        db_status = "unhealthy"

    mqtt = runtime_state.get("mqtt", "unknown")
    sim = runtime_state.get("simulator", "unknown")
    last_ts = last_energy_timestamp(db)
    return HealthOut(
        api="healthy",
        database=db_status,
        mqtt="connected" if mqtt == "connected" else mqtt,
        ml=manager.status(),
        simulator=sim,
        last_data_timestamp=last_ts,
        campus=settings.campus_name,
        data_mode=settings.data_mode,
        details={
            "websocket_clients": ws_manager.connected,
            "last_ingest": runtime_state.get("last_ingest"),
            "mqtt_note": "HTTP ingest fallback is always available at /api/ingest/*",
        },
    )
