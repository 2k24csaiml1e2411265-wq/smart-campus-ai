from pathlib import Path
import threading
import subprocess
import sys

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from starlette.middleware.trustedhost import TrustedHostMiddleware

from app.config import get_settings
from app.database import Base, engine
from app.mqtt.client import start_mqtt, stop_mqtt
from app.routes import admin, anomalies, auth, campus, devices, forecasts, health, ingest, ws
from app.utils.logging import logger

settings = get_settings()
limiter = Limiter(key_func=get_remote_address, default_limits=["120/minute"])


def create_app() -> FastAPI:
    app = FastAPI(
        title="Smart Campus AI",
        description="AI-Powered Energy, Water & Sustainability Intelligence Platform",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

    origins = [o.strip() for o in settings.frontend_url.split(",") if o.strip()]
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
        Path("data").mkdir(exist_ok=True)
        Base.metadata.create_all(bind=engine)
    
        from app.bootstrap import bootstrap
        bootstrap()
    
        start_mqtt()
    
        # Start DEMO simulator in the background
        simulator = Path(__file__).resolve().parents[2] / "simulator" / "simulator.py"
    
        env = os.environ.copy()
        env["SIMULATOR_API_URL"] = "http://127.0.0.1:10000"
    
        subprocess.Popen(
            [sys.executable, str(simulator)],
            env=env,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    
        logger.info("simulator_started", path=str(simulator))
        logger.info("api_started", campus=settings.campus_name, data_mode=settings.data_mode)

    @app.on_event("shutdown")
    def on_shutdown():
        stop_mqtt()

    return app


app = create_app()
