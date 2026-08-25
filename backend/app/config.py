from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(ROOT / ".env", Path(__file__).resolve().parents[1] / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "Smart Campus AI"
    campus_name: str = "PSIT Kanpur"
    data_mode: str = "DEMO"
    environment: str = "development"
    frontend_url: str = "http://localhost:5173,http://127.0.0.1:5173"
    api_base_url: str = "http://localhost:8000"
    log_level: str = "INFO"

    database_url: str = "sqlite:///./data/campus.db"

    supabase_url: str = ""
    supabase_anon_key: str = ""
    supabase_service_role_key: str = ""

    jwt_secret: str = "change-me-to-a-long-random-string"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 480
    simulator_token: str = "demo-simulator-token"

    mqtt_broker: str = "localhost"
    mqtt_port: int = 1883
    mqtt_username: str = ""
    mqtt_password: str = ""
    mqtt_client_id: str = "smart-campus-ai-backend"
    mqtt_enabled: bool = True

    co2_kg_per_kwh: float = 0.82
    co2_factor_source: str = "CEA India grid emission factor (configurable)"

    simulator_interval_seconds: int = 10
    models_dir: str = str(ROOT / "models")


@lru_cache
def get_settings() -> Settings:
    return Settings()
