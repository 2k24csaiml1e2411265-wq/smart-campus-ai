from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.database import SessionLocal, Base, engine
from app.bootstrap import _ensure_catalog
from app.main import app
from tests.conftest import client


def test_empty_latest_ok_after_catalog_only():
    # Dashboard should not crash with available catalog data from session fixture.
    res = client.get("/api/energy/latest")
    assert res.status_code == 200
