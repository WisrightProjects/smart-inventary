"""Structured, per-subsystem logging.

Produces separate rotating log files for camera, AI, database, and general
system events so operators can tail exactly the subsystem they care about.
"""
from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

from backend.config.settings import settings

_LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
_MAX_BYTES = 5 * 1024 * 1024
_BACKUP_COUNT = 3

_configured: dict[str, logging.Logger] = {}


def get_logger(channel: str) -> logging.Logger:
    """Return a logger writing to logs/<channel>.log and stdout.

    channel: one of "camera", "ai", "database", "system" (or any subsystem
    name) — each gets its own rotating file under backend/logs/.
    """
    if channel in _configured:
        return _configured[channel]

    logger = logging.getLogger(f"inventory_ai.{channel}")
    logger.setLevel(logging.DEBUG if settings.debug else logging.INFO)
    logger.propagate = False

    log_path: Path = settings.log_dir / f"{channel}.log"
    file_handler = RotatingFileHandler(
        log_path, maxBytes=_MAX_BYTES, backupCount=_BACKUP_COUNT, encoding="utf-8"
    )
    file_handler.setFormatter(logging.Formatter(_LOG_FORMAT))

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(logging.Formatter(_LOG_FORMAT))

    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)

    _configured[channel] = logger
    return logger
