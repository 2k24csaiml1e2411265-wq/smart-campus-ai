"""Train Isolation Forest from generated or database history."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
sys.path.insert(0, str(ROOT / "simulator"))

from app.database import SessionLocal, Base, engine  # noqa: E402
from app.bootstrap import _ensure_catalog, seed_history, train_from_database  # noqa: E402


def main() -> None:
    Path("data").mkdir(exist_ok=True)
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        _ensure_catalog(db)
        seed_history(db, days=8)
        print(train_from_database(db))
    finally:
        db.close()


if __name__ == "__main__":
    main()
