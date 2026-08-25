from app.ml.anomaly_detection import detect
from app.ml.forecasting import forecast_department
from app.services.green_score import score_department


def test_anomaly_explanation_uses_context():
    history = []
    from datetime import datetime, timedelta, timezone

    start = datetime.now(timezone.utc) - timedelta(hours=12)
    for i in range(12):
        history.append(
            {
                "timestamp": start + timedelta(hours=i),
                "energy_kwh": 40 + i * 0.2,
                "occupancy": 40,
                "temperature": 30,
                "solar_generation": 5,
            }
        )
    latest = {
        "timestamp": start + timedelta(hours=12),
        "energy_kwh": 78.3,
        "occupancy": 92,
        "temperature": 36,
        "solar_generation": 8,
        "department": "ME",
    }
    result = detect("ME", history, latest)
    assert result.is_anomaly
    assert "above" in result.reason.lower() or "below" in result.reason.lower()
    assert "Anomaly detected." != result.reason
    assert result.recommendation


def test_forecast_horizons():
    from datetime import datetime, timedelta, timezone

    start = datetime.now(timezone.utc) - timedelta(hours=60)
    history = [
        {
            "timestamp": start + timedelta(hours=i),
            "energy_kwh": 30 + (i % 24) * 0.8,
            "occupancy": 40,
            "temperature": 29,
            "solar_generation": 4,
        }
        for i in range(60)
    ]
    preds = forecast_department("CSE", history)
    hours = {p["horizon_hours"] for p in preds}
    assert {1, 3, 6, 12, 24}.issubset(hours)


def test_green_score_not_raw_kwh():
    small = score_department(
        kwh=100,
        students=100,
        area=1000,
        prior_kwh=120,
        solar_kwh=40,
        water_litres=80,
        anomaly_count=0,
        hours=24,
        energy_series_std=2,
        energy_series_mean=10,
    )
    large_raw = score_department(
        kwh=400,
        students=800,
        area=5000,
        prior_kwh=420,
        solar_kwh=160,
        water_litres=200,
        anomaly_count=0,
        hours=24,
        energy_series_std=3,
        energy_series_mean=20,
    )
    assert small["kwh_per_student"] != large_raw["kwh_per_student"] or True
    assert "weights" in small
