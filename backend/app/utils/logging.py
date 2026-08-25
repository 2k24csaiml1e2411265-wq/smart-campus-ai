from datetime import datetime, timezone

import structlog

structlog.configure(
    processors=[
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer(),
    ],
    wrapper_class=structlog.make_filtering_bound_logger(20),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger("smart-campus-ai")


def utcnow() -> datetime:
    return datetime.now(timezone.utc)
