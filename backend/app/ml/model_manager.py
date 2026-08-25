from __future__ import annotations

from pathlib import Path

import joblib
import numpy as np
from sklearn.ensemble import IsolationForest, RandomForestRegressor

from app.config import get_settings
from app.utils.logging import logger

settings = get_settings()
MODELS_DIR = Path(settings.models_dir)
MODELS_DIR.mkdir(parents=True, exist_ok=True)

ANOMALY_PATH = MODELS_DIR / "isolation_forest.joblib"
FORECAST_PATH = MODELS_DIR / "energy_forecast.joblib"
METRICS_PATH = MODELS_DIR / "metrics.joblib"


class ModelManager:
    def __init__(self) -> None:
        self.anomaly_model: IsolationForest | None = None
        self.forecast_model: RandomForestRegressor | None = None
        self.metrics: dict = {}
        self.load()

    def load(self) -> None:
        try:
            if ANOMALY_PATH.exists():
                self.anomaly_model = joblib.load(ANOMALY_PATH)
            if FORECAST_PATH.exists():
                self.forecast_model = joblib.load(FORECAST_PATH)
            if METRICS_PATH.exists():
                self.metrics = joblib.load(METRICS_PATH)
            logger.info(
                "ml_models_loaded",
                anomaly=bool(self.anomaly_model),
                forecast=bool(self.forecast_model),
            )
        except Exception as exc:  # pragma: no cover
            logger.error("ml_load_failed", error=str(exc))

    def save_anomaly(self, model: IsolationForest) -> None:
        joblib.dump(model, ANOMALY_PATH)
        self.anomaly_model = model

    def save_forecast(self, model: RandomForestRegressor) -> None:
        joblib.dump(model, FORECAST_PATH)
        self.forecast_model = model

    def save_metrics(self, metrics: dict) -> None:
        joblib.dump(metrics, METRICS_PATH)
        self.metrics = metrics

    @property
    def ready(self) -> bool:
        return self.anomaly_model is not None and self.forecast_model is not None

    def status(self) -> str:
        if self.ready:
            return "ready"
        if self.anomaly_model or self.forecast_model:
            return "partial"
        return "not_trained"


manager = ModelManager()
