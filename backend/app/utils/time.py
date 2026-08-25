from datetime import datetime, timedelta, timezone
from typing import Literal

Period = Literal["24h", "7d", "30d"]


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def period_delta(period: str) -> timedelta:
    mapping = {
        "24h": timedelta(hours=24),
        "today": timedelta(hours=24),
        "7d": timedelta(days=7),
        "30d": timedelta(days=30),
    }
    if period not in mapping:
        raise ValueError("Invalid period. Use 24h, 7d, or 30d.")
    return mapping[period]


def period_start(period: str, end: datetime | None = None) -> datetime:
    end = end or utcnow()
    return end - period_delta(period)
