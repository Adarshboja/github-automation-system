"""Persistence access for generated and created projects."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from github_activity_automation.database.models import CreatedRepository, GeneratedProjectName


class ProjectRepository:
    """Repository for project creator state."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def project_name_exists(self, name: str) -> bool:
        generated = self._session.scalar(
            select(GeneratedProjectName).where(GeneratedProjectName.name == name)
        )
        created = self._session.scalar(
            select(CreatedRepository).where(CreatedRepository.name == name)
        )
        return generated is not None or created is not None

    def record_generated_name(self, name: str, description: str, source: str) -> None:
        if not self.project_name_exists(name):
            self._session.add(
                GeneratedProjectName(
                    name=name,
                    description=description,
                    source=source,
                )
            )

    def record_created_repository(
        self,
        name: str,
        html_url: str,
        language: str,
        description: str,
    ) -> None:
        self._session.add(
            CreatedRepository(
                name=name,
                html_url=html_url,
                language=language,
                description=description,
            )
        )

