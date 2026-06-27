"""Persistence access for commit history."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from github_activity_automation.database.models import CommitHistory


class CommitRepository:
    """Repository for commit records."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def add_commit(
        self,
        repository_name: str,
        commit_sha: str,
        message: str,
        run_id: str,
    ) -> None:
        self._session.add(
            CommitHistory(
                repository_name=repository_name,
                commit_sha=commit_sha,
                message=message,
                run_id=run_id,
            )
        )

    def exists_for_run(self, run_id: str) -> bool:
        statement = select(CommitHistory).where(CommitHistory.run_id == run_id)
        return self._session.scalar(statement) is not None

