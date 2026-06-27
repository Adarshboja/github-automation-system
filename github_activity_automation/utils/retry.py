"""Retry helpers."""

from __future__ import annotations

import logging
import time
from collections.abc import Callable
from typing import TypeVar

logger = logging.getLogger(__name__)
T = TypeVar("T")


def with_retries(
    operation: Callable[[], T],
    retry_count: int,
    backoff_seconds: int,
    operation_name: str,
) -> T:
    """Execute an operation with fixed backoff retries."""

    last_error: Exception | None = None
    for attempt in range(1, retry_count + 1):
        try:
            return operation()
        except Exception as exc:
            last_error = exc
            logger.warning(
                "Operation failed | operation=%s | attempt=%s | error=%s",
                operation_name,
                attempt,
                exc,
            )
            if attempt < retry_count:
                time.sleep(backoff_seconds)
    if last_error:
        raise last_error
    raise RuntimeError(f"Operation failed without exception: {operation_name}")

