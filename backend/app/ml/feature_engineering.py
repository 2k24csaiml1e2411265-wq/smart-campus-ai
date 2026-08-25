"""Feature engineering for energy anomaly detection and forecasting."""

from __future__ import annotations

import numpy as np
import pandas as pd

FEATURE_COLUMNS = [
    "energy_kwh",
    "hour",
    "day_of_week",
    "weekend",
    "rolling_mean",
    "rolling_std",
    "occupancy",
    "temperature",
    "solar_generation",
    "previous_energy",
]

FORECAST_FEATURES = [
    "hour",
    "day_of_week",
    "weekend",
    "previous_energy",
    "rolling_mean",
    "temperature",
    "occupancy",
    "solar_generation",
]


def readings_to_frame(rows: list[dict]) -> pd.DataFrame:
    if not rows:
        return pd.DataFrame(columns=["timestamp", "energy_kwh", "occupancy", "temperature", "solar_generation"])
    df = pd.DataFrame(rows)
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
    df = df.sort_values("timestamp")
    df["hour"] = df["timestamp"].dt.hour
    df["day_of_week"] = df["timestamp"].dt.dayofweek
    df["weekend"] = (df["day_of_week"] >= 5).astype(int)
    df["previous_energy"] = df["energy_kwh"].shift(1).fillna(df["energy_kwh"])
    df["rolling_mean"] = df["energy_kwh"].rolling(6, min_periods=1).mean()
    df["rolling_std"] = df["energy_kwh"].rolling(6, min_periods=1).std().fillna(0)
    if "solar_generation" not in df.columns:
        df["solar_generation"] = 0.0
    if "occupancy" not in df.columns:
        df["occupancy"] = 0
    if "temperature" not in df.columns:
        df["temperature"] = 28.0
    return df


def feature_matrix(df: pd.DataFrame, columns: list[str] | None = None) -> np.ndarray:
    cols = columns or FEATURE_COLUMNS
    missing = [c for c in cols if c not in df.columns]
    if missing:
        raise ValueError(f"Missing feature columns: {missing}")
    return df[cols].astype(float).to_numpy()


def latest_feature_row(df: pd.DataFrame, columns: list[str] | None = None) -> np.ndarray:
    if df.empty:
        raise ValueError("No readings available for features")
    return feature_matrix(df.tail(1), columns)[0:1]
