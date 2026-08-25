"""Actionable recommendations derived from current conditions — no unsupported claims."""

from __future__ import annotations


def from_anomaly(department: str, deviation_pct: float, severity: str, hour: int, contributing: list[str]) -> dict:
    rec = "Inspect HVAC and high-load equipment between 13:00 and 16:00."
    if "high temperature (likely HVAC load)" in contributing:
        rec = f"Inspect HVAC and high-load equipment between {hour:02d}:00 and {(hour + 2) % 24:02d}:00."
    elif deviation_pct < 0:
        rec = "Verify whether scheduled equipment or occupancy sensors are reporting incorrectly."
    return {
        "type": "ANOMALY",
        "department": department,
        "title": f"{department} energy consumption is {abs(deviation_pct):.0f}% {'above' if deviation_pct >= 0 else 'below'} expected.",
        "recommendation": rec,
        "severity": severity,
        "evidence": contributing,
    }


def from_solar(department: str, solar_share: float, hour: int) -> dict | None:
    if 11 <= hour <= 14 and solar_share < 0.18:
        return {
            "type": "SOLAR",
            "department": department,
            "title": f"{department} solar utilization is low during peak irradiance.",
            "recommendation": "Shift flexible loads toward the 11:00–14:00 solar generation window.",
            "severity": "medium",
            "evidence": [f"solar_share={solar_share:.2f}", f"hour={hour}"],
        }
    return None


def from_water(department: str, water_vs_mean: float) -> dict | None:
    if water_vs_mean >= 1.35:
        return {
            "type": "WATER",
            "department": department,
            "title": f"{department} water use is {((water_vs_mean - 1) * 100):.0f}% above recent average.",
            "recommendation": "Check washrooms, labs, and irrigation valves for leaks or overnight flow.",
            "severity": "high" if water_vs_mean >= 1.6 else "medium",
            "evidence": [f"ratio_vs_mean={water_vs_mean:.2f}"],
        }
    return None


def from_score(department: str, total: float, energy_efficiency: float) -> dict | None:
    if total < 55:
        return {
            "type": "SCORE",
            "department": department,
            "title": f"{department} Green Score is {total:.0f}/99.",
            "recommendation": "Prioritize occupancy-based HVAC scheduling and meter-level audits this week.",
            "severity": "medium",
            "evidence": [f"energy_efficiency={energy_efficiency:.1f}"],
        }
    return None
