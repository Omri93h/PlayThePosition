import logging
from typing import Any


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(f"play_the_position.{name}")


def log_event(
    logger: logging.Logger,
    event: str,
    *,
    level: int = logging.INFO,
    **fields: Any,
) -> None:
    logger.log(level, event, extra={"event": event, "fields": fields})
