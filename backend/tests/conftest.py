import os

os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")
os.environ.setdefault("JWT_SECRET", "test-secret")
os.environ.setdefault("MQTT_ENABLED", "false")

from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker

from app.database import Base, engine, get_db
from app.main import app
from app.bootstrap import _ensure_catalog, seed_history
from app.database import SessionLocal


def _prepare():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    _ensure_catalog(db)
    seed_history(db, days=3)
    db.close()


_prepare()
client = TestClient(app)
AUTH = None


def login(email="admin@psit.ac.in", password="admin123"):
    res = client.post("/api/auth/login", json={"email": email, "password": password})
    assert res.status_code == 200, res.text
    return res.json()["access_token"]
