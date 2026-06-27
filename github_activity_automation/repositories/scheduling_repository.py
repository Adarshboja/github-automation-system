"""Persistence access for scheduling metadata."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from github_activity_automation.database.models import SchedulingMetadata


class SchedulingRepository:
    """Repository for scheduler metadata."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def upsert_job(
        self,
        job_name: str,
        cron_expression: str,
        timezone: str,
        enabled: bool,
    ) -> None:
        existing = self._session.scalar(
            select(SchedulingMetadata).where(SchedulingMetadata.job_name == job_name)
        )
        if existing:
            existing.cron_expression = cron_expression
            existing.timezone = timezone
            existing.enabled = enabled
            return
        self._session.add(
            SchedulingMetadata(
                job_name=job_name,
                cron_expression=cron_expression,
                timezone=timezone,
                enabled=enabled,
            )
        )

