from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_db
from app.schemas import DeviceHeartbeatIn, EnergyReadingIn, EnvironmentReadingIn, SolarReadingIn, WaterReadingIn
from app.services.ingestion import ingest_energy, ingest_environment, ingest_heartbeat, ingest_solar, ingest_water
from app.services.realtime import mark_simulator

router = APIRouter(prefix="/ingest", tags=["ingest"])
settings = get_settings()


def _auth(x_simulator_token: str | None):
    if x_simulator_token != settings.simulator_token:
        raise HTTPException(status_code=401, detail="Invalid simulator token")


@router.post("/energy")
def energy(body: EnergyReadingIn, db: Session = Depends(get_db), x_simulator_token: str | None = Header(default=None)):
    _auth(x_simulator_token)
    try:
        return ingest_energy(db, body.model_dump())
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.post("/solar")
def solar(body: SolarReadingIn, db: Session = Depends(get_db), x_simulator_token: str | None = Header(default=None)):
    _auth(x_simulator_token)
    ingest_solar(db, body.model_dump())
    return {"ok": True}


@router.post("/water")
def water(body: WaterReadingIn, db: Session = Depends(get_db), x_simulator_token: str | None = Header(default=None)):
    _auth(x_simulator_token)
    ingest_water(db, body.model_dump())
    return {"ok": True}


@router.post("/environment")
def environment(
    body: EnvironmentReadingIn, db: Session = Depends(get_db), x_simulator_token: str | None = Header(default=None)
):
    _auth(x_simulator_token)
    ingest_environment(db, body.model_dump())
    return {"ok": True}


@router.post("/device")
def device(body: DeviceHeartbeatIn, db: Session = Depends(get_db), x_simulator_token: str | None = Header(default=None)):
    _auth(x_simulator_token)
    ingest_heartbeat(db, body.model_dump())
    mark_simulator("running")
    return {"ok": True}
