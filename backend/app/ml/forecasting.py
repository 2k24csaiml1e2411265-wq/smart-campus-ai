"""Random Forest energy forecasting. Deep learning is intentionally not used."""

from __future__ import annotations

from datetime import timedelta

import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error

from app.ml.feature_engineering import FORECAST_FEATURES, feature_matrix, readings_to_frame
from app.ml.model_manager import manager
from app.utils.time import utcnow

HORIZONS = [1, 3, 6, 12, 24]


def _mape(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    mask = y_true != 0
    if not mask.any():
        return 0.0
    return float(np.mean(np.abs((y_true[mask] - y_pred[mask]) / y_true[mask])) * 100)


def train_forecast(rows: list[dict]) -> RandomForestRegressor:
    df = readings_to_frame(rows)
    if len(df) < 48:
        raise ValueError("Need at least 48 historical points to train forecast model")
    X = feature_matrix(df.iloc[:-1], FORECAST_FEATURES)
    y = df["energy_kwh"].iloc[1:].to_numpy()
    split = int(len(X) * 0.8)
    X_train, X_test = X[:split], X[split:]
    y_train, y_test = y[:split], y[split:]
    model = RandomForestRegressor(
        n_estimators=180,
        max_depth=12,
        random_state=42,
        n_jobs=-1,
        min_samples_leaf=2,
    )
    model.fit(X_train, y_train)
    preds = model.predict(X_test) if len(X_test) else model.predict(X_train)
    truth = y_test if len(X_test) else y_train
    mae = float(mean_absolute_error(truth, preds))
    rmse = float(np.sqrt(mean_squared_error(truth, preds)))
    mape = _mape(truth, preds)
    residual_std = float(np.std(truth - preds)) if len(truth) else 1.0
    metrics = {
        "forecast": {
            "mae": mae,
            "rmse": rmse,
            "mape": mape,
            "residual_std": residual_std,
            "model_name": "RandomForestRegressor",
            "train_size": int(len(X_train)),
            "test_size": int(len(X_test)),
            "note": "Hold-out evaluation on simulated historical series. Not a claim of real campus accuracy.",
        }
    }
    existing = manager.metrics or {}
    existing.update(metrics)
    manager.save_metrics(existing)
    manager.save_forecast(model)
    return model


def forecast_department(department: str, history: list[dict], horizons: list[int] | None = None) -> list[dict]:
    horizons = horizons or HORIZONS
    df = readings_to_frame(history)
    if df.empty:
        return []
    model = manager.forecast_model
    residual_std = float((manager.metrics or {}).get("forecast", {}).get("residual_std", 4.0))
    now = utcnow()
    last = df.iloc[-1].copy()
    results = []
    energy = float(last["energy_kwh"])
    for h in range(1, max(horizons) + 1):
        ts = now + timedelta(hours=h)
        last["hour"] = ts.hour
        last["day_of_week"] = ts.weekday()
        last["weekend"] = int(ts.weekday() >= 5)
        last["previous_energy"] = energy
        X = feature_matrix(last.to_frame().T, FORECAST_FEATURES)
        if model is None:
            pred = energy * (0.92 + 0.15 * np.sin((ts.hour - 8) / 24 * np.pi))
            model_name = "heuristic_fallback"
            confidence = 0.45
        else:
            pred = float(model.predict(X)[0])
            model_name = "RandomForestRegressor"
            confidence = 0.82
        energy = max(pred, 0.1)
        last["energy_kwh"] = energy
        last["rolling_mean"] = 0.7 * float(last.get("rolling_mean", energy)) + 0.3 * energy
        if h in horizons:
            band = residual_std * (1.0 + 0.08 * h)
            results.append(
                {
                    "department_code": department,
                    "timestamp": now,
                    "forecast_for": ts,
                    "predicted_kwh": round(float(pred), 2),
                    "lower_bound": round(max(float(pred) - 1.64 * band, 0), 2),
                    "upper_bound": round(float(pred) + 1.64 * band, 2),
                    "model_name": model_name,
                    "horizon_hours": h,
                    "confidence": confidence,
                }
            )
    return results
