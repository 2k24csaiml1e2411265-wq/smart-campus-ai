from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timedelta

from fastapi import WebSocket

from app.utils.logging import logger
from app.utils.time import utcnow


class ConnectionManager:
    def __init__(self) -> None:
        self.active: list[WebSocket] = []
        self.last_broadcast: datetime | None = None

    async def connect(self, ws: WebSocket) -> None:
        await ws.accept()
        self.active.append(ws)

    def disconnect(self, ws: WebSocket) -> None:
        if ws in self.active:
            self.active.remove(ws)

    async def broadcast(self, message: dict) -> None:
        self.last_broadcast = utcnow()
        stale = []
        for ws in self.active:
            try:
                await ws.send_json(message)
            except Exception:
                stale.append(ws)
        for ws in stale:
            self.disconnect(ws)

    @property
    def connected(self) -> int:
        return len(self.active)


ws_manager = ConnectionManager()

# Simple TTL cache for dashboard payloads
_cache: dict[str, tuple[datetime, dict]] = {}


def cache_get(key: str, ttl_seconds: int = 8) -> dict | None:
    hit = _cache.get(key)
    if not hit:
        return None
    ts, value = hit
    if utcnow() - ts > timedelta(seconds=ttl_seconds):
        _cache.pop(key, None)
        return None
    return value


def cache_set(key: str, value: dict) -> None:
    _cache[key] = (utcnow(), value)


def cache_clear() -> None:
    _cache.clear()


# Runtime flags used by health checks
runtime_state = defaultdict(lambda: "unknown")
runtime_state.update(
    {
        "mqtt": "disconnected",
        "simulator": "unknown",
        "last_ingest": None,
    }
)


def mark_simulator(status: str) -> None:
    runtime_state["simulator"] = status
    runtime_state["simulator_seen"] = utcnow().isoformat()
    logger.info("simulator_status", status=status)
