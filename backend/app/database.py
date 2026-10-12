
from sqlalchemy import create_engine, event
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.config import get_settings

settings = get_settings()
database_url = settings.database_url

connect_args = {}

if database_url.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

elif database_url.startswith(
    ("postgresql://", "postgresql+psycopg2://")
):
    connect_args = {"sslmode": "require"}

engine = create_engine(
    database_url,
    connect_args=connect_args,
    pool_pre_ping=True,
    future=True,
)

if database_url.startswith("sqlite"):

    @event.listens_for(engine, "connect")
    def _sqlite_pragma(dbapi_connection, _connection_record):
        cursor = dbapi_connection.cursor()
        try:
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.execute("PRAGMA journal_mode=WAL")
        finally:
            cursor.close()


SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    future=True,
)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
