from __future__ import annotations

import logging
from typing import Final

import structlog

_LEVEL_TO_INT: Final[dict[str, int]] = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL,
}

_CONFIGURED = False


def configure_logging(level: str = "INFO") -> None:
    global _CONFIGURED
    if _CONFIGURED:
        return

    normalized_level = level.upper()
    level_value = _LEVEL_TO_INT.get(normalized_level, logging.INFO)

    logging.basicConfig(level=level_value, format="%(message)s")

    structlog.configure(
        processors=[
            structlog.processors.TimeStamper(fmt="iso", utc=True),
            structlog.processors.add_log_level,
            structlog.processors.JSONRenderer(sort_keys=True),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(level_value),
        cache_logger_on_first_use=True,
    )
    _CONFIGURED = True


def get_logger() -> structlog.stdlib.BoundLogger:
    return structlog.get_logger("medlabs_sdk")
