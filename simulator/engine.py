"""Realistic (illustrative) campus sensor physics. DEMO/SIMULATED only."""

from __future__ import annotations

import math
import random
from datetime import datetime, timezone

from copy import deepcopy

# Imported by backend seed as well
try:
    from app.utils.campus import DEPARTMENTS, devices_for
except ImportError:  # running as standalone simulator
    DEPARTMENTS = None
    devices_for = None


def _hour_profile(hour: int, weekend: bool) -> float:
    if weekend:
        if 8 <= hour <= 16:
            return 0.45
        if 17 <= hour <= 21:
            return 0.28
        return 0.12
    if 8 <= hour <= 10:
        return 0.85
    if 11 <= hour <= 13:
        return 1.05
    if 14 <= hour <= 17:
        return 1.18
    if 18 <= hour <= 20:
        return 0.55
    if 21 <= hour <= 23:
        return 0.22
    return 0.12


def _occupancy(hour: int, weekend: bool, students: int) -> int:
    frac = _hour_profile(hour, weekend)
    noise = random.uniform(0.85, 1.12)
    return int(max(0, students * 0.35 * frac * noise))


def _temperature(hour: int) -> float:
    return 26.5 + 7.5 * math.sin((hour - 9) / 24 * math.pi * 2 / 1.6) + random.uniform(-0.8, 0.8)


def _humidity(hour: int) -> float:
    return max(28.0, min(78.0, 55 - 8 * math.sin(hour / 24 * math.pi) + random.uniform(-4, 4)))


def _irradiance(hour: int, weather: float) -> float:
    if hour < 6 or hour > 18:
        return 0.0
    bell = math.sin((hour - 6) / 12 * math.pi)
    return max(0.0, 980 * bell * weather + random.uniform(-20, 20))


def generate_tick(dept: dict, ts: datetime, anomaly: bool = False, weather: float = 0.92) -> dict:
    hour = ts.hour
    weekend = ts.weekday() >= 5
    occ = _occupancy(hour, weekend, dept["student_count"])
    temp = _temperature(hour)
    profile = _hour_profile(hour, weekend)
    temp_load = max(0, temp - 28) * 0.9
    occ_load = occ / max(dept["student_count"], 1) * 18
    energy = dept["energy_base"] * profile + temp_load + occ_load + random.gauss(0, 1.4)
    energy = max(2.5, energy)
    if anomaly:
        energy *= random.uniform(1.55, 1.95)

    irr = _irradiance(hour, weather)
    solar = dept["solar_cap"] * (irr / 900.0) * random.uniform(0.92, 1.05)
    solar = max(0.0, solar)

    water = dept["water_base"] * (0.25 + occ / max(dept["student_count"], 1)) * (1.1 if 10 <= hour <= 16 else 0.6)
    water += random.gauss(0, 4)
    water = max(5.0, water)
    if anomaly and random.random() < 0.3:
        water *= 1.7

    voltage = 230 + random.uniform(-4, 4)
    current = (energy * 1000 / max(voltage, 1)) / 3
    pf = min(0.98, max(0.78, 0.91 + random.uniform(-0.05, 0.04)))
    flow = water / 60.0
    pressure = 3.2 + random.uniform(-0.3, 0.3)

    code = dept["code"]
    return {
        "timestamp": ts,
        "department": code,
        "occupancy": occ,
        "temperature": round(temp, 2),
        "humidity": round(_humidity(hour), 2),
        "energy": {
            "energy_kwh": round(energy, 2),
            "voltage": round(voltage, 2),
            "current": round(current, 2),
            "power_factor": round(pf, 3),
            "temperature": round(temp, 2),
            "occupancy": occ,
            "is_simulated": True,
            "is_anomaly_injected": anomaly,
        },
        "solar": {
            "solar_kwh": round(solar, 2),
            "voltage": round(voltage + 8, 2),
            "current": round(max(solar * 1000 / max(voltage, 1) / 3, 0), 2),
            "irradiance": round(irr, 1),
            "is_simulated": True,
        },
        "water": {
            "water_litres": round(water, 2),
            "flow_rate": round(flow, 3),
            "pressure": round(pressure, 2),
            "is_simulated": True,
            "is_anomaly_injected": anomaly,
        },
        "environment": {
            "temperature": round(temp, 2),
            "humidity": round(_humidity(hour), 2),
            "occupancy": occ,
            "is_simulated": True,
        },
        "devices": [
            {"device_id": f"{code}-F1-ENERGY-01", "kind": "energy", "share": 0.55},
            {"device_id": f"{code}-F2-ENERGY-02", "kind": "energy", "share": 0.45},
            {"device_id": f"{code}-SOLAR-01", "kind": "solar", "share": 1.0},
            {"device_id": f"{code}-WATER-01", "kind": "water", "share": 1.0},
            {"device_id": f"{code}-ENV-01", "kind": "environment", "share": 1.0},
        ],
    }
