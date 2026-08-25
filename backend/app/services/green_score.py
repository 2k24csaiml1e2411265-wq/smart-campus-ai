"""Normalized Green Score. Departments are not ranked by raw kWh."""

from __future__ import annotations

WEIGHTS = {
    "energy_efficiency": 0.35,
    "energy_reduction": 0.25,
    "solar_utilization": 0.15,
    "water_efficiency": 0.10,
    "anomaly_rate": 0.10,
    "consistency": 0.05,
}


def _clamp(value: float, lo: float = 0, hi: float = 99) -> float:
    return max(lo, min(hi, value))


def score_department(
    *,
    kwh: float,
    students: int,
    area: float,
    prior_kwh: float,
    solar_kwh: float,
    water_litres: float,
    anomaly_count: int,
    hours: int,
    energy_series_std: float,
    energy_series_mean: float,
) -> dict:
    kwh_per_student = kwh / max(students, 1)
    kwh_per_sqm = kwh / max(area, 1)

    # Lower intensity is better. Typical simulated campus range is used only as a scale, not a real benchmark.
    efficiency = _clamp(99 - kwh_per_student * 8 - kwh_per_sqm * 40)
    if prior_kwh > 0:
        reduction_pct = (prior_kwh - kwh) / prior_kwh
        reduction = _clamp(50 + reduction_pct * 200)
    else:
        reduction = 60.0
    solar_share = solar_kwh / max(kwh, 0.01)
    solar = _clamp(solar_share * 180)
    water_per_person = water_litres / max(students, 1)
    water = _clamp(99 - water_per_person * 0.35)
    expected_hours = max(hours / 24, 1)
    anomaly_rate = anomaly_count / expected_hours
    anomaly = _clamp(99 - anomaly_rate * 25)
    cv = energy_series_std / energy_series_mean if energy_series_mean else 0
    consistency = _clamp(99 - cv * 80)

    total = (
        efficiency * WEIGHTS["energy_efficiency"]
        + reduction * WEIGHTS["energy_reduction"]
        + solar * WEIGHTS["solar_utilization"]
        + water * WEIGHTS["water_efficiency"]
        + anomaly * WEIGHTS["anomaly_rate"]
        + consistency * WEIGHTS["consistency"]
    )
    total = _clamp(total)
    carbon = _clamp(solar)  # solar-driven avoided emissions share

    return {
        "energy_score": round(efficiency, 1),
        "solar_score": round(solar, 1),
        "water_score": round(water, 1),
        "carbon_score": round(carbon, 1),
        "anomaly_score": round(anomaly, 1),
        "consistency_score": round(consistency, 1),
        "energy_efficiency": round(efficiency, 1),
        "energy_reduction": round(reduction, 1),
        "total_score": round(total, 1),
        "kwh_per_student": round(kwh_per_student, 3),
        "kwh_per_sqm": round(kwh_per_sqm, 4),
        "weights": WEIGHTS,
    }
