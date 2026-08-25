#!/usr/bin/env python3
"""IoT simulator for Smart Campus AI. DEMO data only — not physical sensors."""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT.parent / "backend"))

from engine import generate_tick  # noqa: E402

try:
    from app.utils.campus import DEPARTMENTS
except Exception:
    DEPARTMENTS = [
        {"code": "CSE", "student_count": 720, "energy_base": 42, "solar_cap": 28, "water_base": 180, "name": "CSE"},
        {"code": "ECE", "student_count": 540, "energy_base": 38, "solar_cap": 22, "water_base": 150, "name": "ECE"},
        {"code": "ME", "student_count": 480, "energy_base": 55, "solar_cap": 18, "water_base": 210, "name": "ME"},
        {"code": "CE", "student_count": 420, "energy_base": 33, "solar_cap": 16, "water_base": 190, "name": "CE"},
        {"code": "MBA", "student_count": 240, "energy_base": 22, "solar_cap": 12, "water_base": 90, "name": "MBA"},
        {"code": "MCA", "student_count": 180, "energy_base": 20, "solar_cap": 10, "water_base": 70, "name": "MCA"},
        {"code": "EEE", "student_count": 360, "energy_base": 48, "solar_cap": 24, "water_base": 160, "name": "EEE"},
    ]

API = os.environ.get("SIMULATOR_API_URL", os.environ.get("API_BASE_URL", "http://localhost:8000"))
TOKEN = os.environ.get("SIMULATOR_TOKEN", "demo-simulator-token")
MQTT_BROKER = os.environ.get("MQTT_BROKER", "localhost")
MQTT_PORT = int(os.environ.get("MQTT_PORT", "1883"))


def publish_mqtt(topic: str, payload: dict) -> bool:
    try:
        import paho.mqtt.client as mqtt

        client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        user = os.environ.get("MQTT_USERNAME")
        if user:
            client.username_pw_set(user, os.environ.get("MQTT_PASSWORD", ""))
        client.connect(MQTT_BROKER, MQTT_PORT, 5)
        client.publish(topic, json.dumps(payload, default=str), qos=0)
        client.disconnect()
        return True
    except Exception:
        return False


def post(path: str, payload: dict) -> None:
    headers = {"X-Simulator-Token": TOKEN}
    body = {**payload}
    if isinstance(body.get("timestamp"), datetime):
        body["timestamp"] = body["timestamp"].isoformat()
    httpx.post(f"{API}{path}", json=body, headers=headers, timeout=8.0)


def emit(tick: dict, use_mqtt: bool) -> None:
    dept = tick["department"].lower()
    energy = tick["energy"]
    # split across two meters
    for device, share in ((f"{tick['department']}-F1-ENERGY-01", 0.55), (f"{tick['department']}-F2-ENERGY-02", 0.45)):
        payload = {
            "device_id": device,
            "department": tick["department"],
            "timestamp": tick["timestamp"],
            **energy,
            "energy_kwh": round(energy["energy_kwh"] * share, 2),
        }
        topic = f"campus/{dept}/energy"
        sent = use_mqtt and publish_mqtt(topic, payload)
        if not sent:
            post("/api/ingest/energy", payload)
    solar = {
        "device_id": f"{tick['department']}-SOLAR-01",
        "department": tick["department"],
        "timestamp": tick["timestamp"],
        **tick["solar"],
    }
    if not (use_mqtt and publish_mqtt(f"campus/{dept}/solar", solar)):
        post("/api/ingest/solar", solar)
    water = {
        "device_id": f"{tick['department']}-WATER-01",
        "department": tick["department"],
        "timestamp": tick["timestamp"],
        **tick["water"],
    }
    if not (use_mqtt and publish_mqtt(f"campus/{dept}/water", water)):
        post("/api/ingest/water", water)
    env = {
        "device_id": f"{tick['department']}-ENV-01",
        "department": tick["department"],
        "timestamp": tick["timestamp"],
        **tick["environment"],
    }
    if not (use_mqtt and publish_mqtt(f"campus/{dept}/environment", env)):
        post("/api/ingest/environment", env)


def main() -> None:
    parser = argparse.ArgumentParser(description="Smart Campus AI IoT simulator (DEMO)")
    parser.add_argument("--interval", type=int, default=int(os.environ.get("SIMULATOR_INTERVAL_SECONDS", "10")))
    parser.add_argument("--anomaly", action="store_true", help="Inject abnormal consumption")
    parser.add_argument("--once", action="store_true")
    parser.add_argument("--mqtt", action="store_true", help="Prefer MQTT; HTTP fallback always exists")
    args = parser.parse_args()
    print("Smart Campus AI simulator — DEMO/SIMULATED DATA (not physical IoT hardware)")
    print(f"API={API} interval={args.interval}s anomaly={args.anomaly}")
    while True:
        ts = datetime.now(timezone.utc)
        for spec in DEPARTMENTS:
            force = args.anomaly and spec.get("code") in {"ME", "CSE"}
            tick = generate_tick(spec, ts, anomaly=force)
            try:
                emit(tick, use_mqtt=args.mqtt)
            except Exception as exc:
                print("ingest failed", spec.get("code"), exc)
        if args.once:
            break
        time.sleep(max(args.interval, 2))


if __name__ == "__main__":
    main()
