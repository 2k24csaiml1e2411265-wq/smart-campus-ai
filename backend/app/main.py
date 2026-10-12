
from pathlib import Path
import subprocess
import sys
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.engine import make_url
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from app.config import get_settings
from app.database import Base, engine
from app.mqtt.client import start_mqtt, stop_mqtt
from app.routes import (
    admin,
    anomalies,
    auth,
    campus,
    devices,
    forecasts,
    health,
    ingest,
    ws,
)
from app.utils.logging import logger

settings = get_settings()
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["120/minute"],
)


def create_app() -> FastAPI:
    app = FastAPI(
        title="Smart Campus AI",
        description=(
            "AI-Powered Energy, Water & Sustainability Intelligence Platform"
        ),
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    app.state.limiter = limiter
    app.add_exception_handler(
        RateLimitExceeded,
        _rate_limit_exceeded_handler,
    )

    origins = [
        origin.strip()
        for origin in settings.frontend_url.split(",")
        if origin.strip()
    ]

    if not origins:
        origins = ["http://localhost:5173"]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    api = "/api"

    app.include_router(health.router, prefix=api)
    app.include_router(auth.router, prefix=api)
    app.include_router(ingest.router, prefix=api)
    app.include_router(campus.router, prefix=api)
    app.include_router(anomalies.router, prefix=api)
    app.include_router(forecasts.router, prefix=api)
    app.include_router(devices.router, prefix=api)
    app.include_router(admin.router, prefix=api)
    app.include_router(ws.router, prefix=api)

    @app.on_event("startup")
    def on_startup():
        logger.info(
            "database_config",
            driver=engine.url.drivername,
            host=engine.url.host,
            port=engine.url.port,
            database=engine.url.database,
        )

        # Create a local data directory if needed.
        # SQLite uses it; PostgreSQL does not require it.
        Path("data").mkdir(parents=True, exist_ok=True)

        # Fail clearly if the database cannot be reached.
        try:
            with engine.connect() as connection:
                connection.execute(
                    __import__("sqlalchemy").text("SELECT 1")
                )

            logger.info("database_connection_success")

            Base.metadata.create_all(bind=engine)

            from app.bootstrap import bootstrap
            bootstrap()

        except Exception:
            logger.exception("database_startup_failed")
            raise

        # Start MQTT without preventing HTTP fallback.
        try:
            start_mqtt()
        except Exception:
            logger.exception("mqtt_start_failed")

        # Start the demo simulator if the script exists.
        simulator = (
            Path(__file__).resolve().parents[2]
            / "simulator"
            / "simulator.py"
        )

        if simulator.exists():
            env = os.environ.copy()

            # Configure API_BASE_URL in Render to point to this backend.
            env["SIMULATOR_API_URL"] = (
                settings.api_base_url.rstrip("/")
            )

            try:
                subprocess.Popen(
                    [sys.executable, str(simulator)],
                    env=env,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )

                logger.info(
                    "simulator_started",
                    path=str(simulator),
                )
            except Exception:
                logger.exception("simulator_start_failed")
        else:
            logger.warning(
                "simulator_not_found",
                path=str(simulator),
            )

        logger.info(
            "api_started",
            campus=settings.campus_name,
            data_mode=settings.data_mode,
        )

    @app.on_event("shutdown")
    def on_shutdown():
        try:
            stop_mqtt()
        except Exception:
            logger.exception("mqtt_stop_failed")

    return app


app = create_app()
