"""Isolation Forest anomaly detection with data-driven explanations."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest

from app.ml.feature_engineering import FEATURE_COLUMNS, feature_matrix, readings_to_frame
from app.ml.model_manager import manager


@dataclass
class AnomalyResult:
    is_anomaly: bool
    anomaly_score: float
    expected: float
    actual: float
    severity: str
    reason: str
    recommendation: str
    department: str
    contributing: list[str]


def _severity(score: float, deviation_pct: float) -> str:
    if score < -0.55 or deviation_pct >= 45:
        return "critical"
    if score < -0.35 or deviation_pct >= 30:
        return "high"
    if score < -0.15 or deviation_pct >= 18:
        return "medium"
    return "low"


def _explain(row: pd.Series, expected: float, actual: float) -> tuple[str, list[str]]:
    deviation = ((actual - expected) / expected * 100) if expected else 0
    direction = "above" if actual >= expected else "below"
    factors: list[str] = []
    hour = int(row.get("hour", 0))
    if row.get("occupancy", 0) >= 80:
        factors.append("high occupancy")
    if row.get("temperature", 0) >= 34:
        factors.append("high temperature (likely HVAC load)")
    if 13 <= hour <= 16:
        factors.append("unusual afternoon load")
    if actual > row.get("rolling_mean", actual) + 1.5 * max(row.get("rolling_std", 1), 1):
        factors.append("historical rolling peak exceeded")
    if row.get("weekend", 0) == 1 and actual > expected:
        factors.append("weekend consumption higher than typical")
    if not factors:
        factors.append("deviation from learned seasonal pattern")
    reason = (
        f"{row.get('department', 'Department')} energy consumption is {abs(deviation):.1f}% {direction} "
        f"its expected value for this time period.\n\nPossible contributing factors:\n"
        + "\n".join(f"* {f}" for f in factors)
    )
    return reason, factors


def _recommend(factors: list[str], hour: int, deviation_pct: float) -> str:
    if deviation_pct < 0:
        return "Review whether scheduled equipment was offline unexpectedly; confirm occupancy sensors."
    if "high temperature (likely HVAC load)" in factors:
        return f"Inspect HVAC setpoints and high-load equipment between {hour:02d}:00 and {(hour + 2) % 24:02d}:00."
    if "unusual afternoon load" in factors:
        return "Inspect HVAC and high-load equipment between 13:00 and 16:00."
    if "weekend consumption higher than typical" in factors:
        return "Audit weekend lab/workshop equipment left running; enable scheduled shutdowns."
    return f"Inspect high-load circuits around {hour:02d}:00 and compare against occupancy schedules."


def train_isolation_forest(rows: list[dict], contamination: float = 0.04) -> IsolationForest:
    df = readings_to_frame(rows)
    X = feature_matrix(df, FEATURE_COLUMNS)
    model = IsolationForest(
        n_estimators=200,
        contamination=contamination,
        random_state=42,
        n_jobs=-1,
    )
    model.fit(X)
    manager.save_anomaly(model)
    return model


def detect(department: str, history: list[dict], latest: dict) -> AnomalyResult:
    rows = history + [latest]
    df = readings_to_frame(rows)
    df["department"] = department
    actual = float(latest["energy_kwh"])
    expected = float(df["rolling_mean"].iloc[-1]) if not df.empty else actual
    if expected <= 0:
        expected = actual
    score = 0.0
    is_anomaly = False
    model = manager.anomaly_model
    if model is not None and len(df) >= 4:
        X = feature_matrix(df.tail(1), FEATURE_COLUMNS)
        raw = model.decision_function(X)[0]
        pred = model.predict(X)[0]
        score = float(raw)
        is_anomaly = bool(pred == -1)
    deviation_pct = ((actual - expected) / expected * 100) if expected else 0
    if abs(deviation_pct) >= 25:
        is_anomaly = True
    row = df.iloc[-1]
    reason, factors = _explain(row, expected, actual)
    severity = _severity(score if is_anomaly else 0.1, abs(deviation_pct))
    if not is_anomaly:
        severity = "low"
        reason = f"{department} consumption is within expected bounds ({abs(deviation_pct):.1f}% vs rolling mean)."
    return AnomalyResult(
        is_anomaly=is_anomaly,
        anomaly_score=round(score, 4),
        expected=round(expected, 2),
        actual=round(actual, 2),
        severity=severity,
        reason=reason,
        recommendation=_recommend(factors, int(row.get("hour", 12)), deviation_pct),
        department=department,
        contributing=factors,
    )


def evaluate_with_labels(X: np.ndarray, y_true: np.ndarray) -> dict:
    """Evaluate using synthetic labels. Isolation Forest is unsupervised; labels are injected for demo eval only."""
    from sklearn.metrics import confusion_matrix, f1_score, precision_score, recall_score

    if manager.anomaly_model is None:
        raise RuntimeError("Anomaly model is not trained")
    y_pred = (manager.anomaly_model.predict(X) == -1).astype(int)
    tn, fp, fn, tp = confusion_matrix(y_true, y_pred, labels=[0, 1]).ravel()
    return {
        "precision": float(precision_score(y_true, y_pred, zero_division=0)),
        "recall": float(recall_score(y_true, y_pred, zero_division=0)),
        "f1": float(f1_score(y_true, y_pred, zero_division=0)),
        "confusion_matrix": {"tn": int(tn), "fp": int(fp), "fn": int(fn), "tp": int(tp)},
        "note": "Labels are synthetic (injected anomalies). Isolation Forest is unsupervised; these metrics are not campus-measured accuracy.",
    }
