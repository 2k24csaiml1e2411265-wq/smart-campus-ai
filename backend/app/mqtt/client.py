import json
from typing import Callable

import paho.mqtt.client as mqtt

from app.config import get_settings
from app.database import SessionLocal
from app.services.ingestion import ingest_energy, ingest_environment, ingest_heartbeat, ingest_solar, ingest_water
from app.services.realtime import runtime_state
from app.utils.logging import logger

settings = get_settings()
_client: mqtt.Client | None = None


def _on_connect(client, userdata, flags, reason_code, properties=None):
    runtime_state["mqtt"] = "connected"
    logger.info("mqtt_connected", code=str(reason_code))
    client.subscribe("campus/+/energy")
    client.subscribe("campus/+/solar")
    client.subscribe("campus/+/water")
    client.subscribe("campus/+/environment")
    client.subscribe("campus/+/device")


def _on_disconnect(client, userdata, *args):
    runtime_state["mqtt"] = "disconnected"
    logger.info("mqtt_disconnected")


def _handle(topic: str, payload: dict) -> None:
    parts = topic.split("/")
    if len(parts) < 3:
        return
    kind = parts[2]
    db = SessionLocal()
    try:
        if kind == "energy":
            ingest_energy(db, payload)
        elif kind == "solar":
            ingest_solar(db, payload)
        elif kind == "water":
            ingest_water(db, payload)
        elif kind == "environment":
            ingest_environment(db, payload)
        elif kind == "device":
            ingest_heartbeat(db, payload)
        logger.info("mqtt_ingest", topic=topic)
    except Exception as exc:
        logger.error("mqtt_ingest_failed", topic=topic, error=str(exc))
    finally:
        db.close()


def _on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode("utf-8"))
    except json.JSONDecodeError:
        logger.error("mqtt_bad_json", topic=msg.topic)
        return
    _handle(msg.topic, payload)


def start_mqtt() -> None:
    global _client
    if not settings.mqtt_enabled:
        runtime_state["mqtt"] = "disabled"
        return
    try:
        _client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=settings.mqtt_client_id)
        if settings.mqtt_username:
            _client.username_pw_set(settings.mqtt_username, settings.mqtt_password)
        _client.on_connect = _on_connect
        _client.on_disconnect = _on_disconnect
        _client.on_message = _on_message
        _client.connect_async(settings.mqtt_broker, settings.mqtt_port, 60)
        _client.loop_start()
        runtime_state["mqtt"] = "connecting"
    except Exception as exc:
        runtime_state["mqtt"] = "unavailable"
        logger.info("mqtt_unavailable_http_fallback", error=str(exc))


def stop_mqtt() -> None:
    global _client
    if _client:
        try:
            _client.loop_stop()
            _client.disconnect()
        except Exception:
            pass
        _client = None
