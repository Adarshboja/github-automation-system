"""Application logging setup."""

from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

from github_activity_automation.config.settings import LoggingSettings


class StructuredFormatter(logging.Formatter):
    """Format logs with timestamp, severity, logger, and message."""

    def format(self, record: logging.LogRecord) -> str:
        base = super().format(record)
        return base


def configure_logging(settings: LoggingSettings) -> None:
    """Configure console and rotating file logging."""

    log_dir = Path(settings.directory)
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / settings.filename
    level = getattr(logging, settings.level.upper(), logging.INFO)
    formatter = StructuredFormatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )

    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    root_logger.handlers.clear()

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(level)

    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=settings.max_bytes,
        backupCount=settings.backup_count,
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(level)

    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)

