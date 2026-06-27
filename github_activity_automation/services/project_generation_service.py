"""Project idea generation and duplicate prevention."""

from __future__ import annotations

import logging

from github_activity_automation.config.settings import ProjectCreatorSettings
from github_activity_automation.exceptions import AIServiceError
from github_activity_automation.repositories.project_repository import ProjectRepository
from github_activity_automation.services.ai_service import AIService

logger = logging.getLogger(__name__)


class ProjectGenerationService:
    """Generate unique project names with AI fallback."""

    def __init__(
        self,
        settings: ProjectCreatorSettings,
        ai_service: AIService,
        project_repository: ProjectRepository,
    ) -> None:
        self._settings = settings
        self._ai_service = ai_service
        self._project_repository = project_repository

    def generate_unique_project(self) -> tuple[str, str, str]:
        """Return name, description, and source."""

        try:
            name, description = self._ai_service.generate_project_idea(
                self._settings.language
            )
            if not self._project_repository.project_name_exists(name):
                return name, description, "ai"
            logger.info("AI generated duplicate project name: %s", name)
        except AIServiceError as exc:
            logger.warning("AI project generation failed; using fallback | error=%s", exc)

        for idea in self._settings.fallback_project_ideas:
            if not self._project_repository.project_name_exists(idea.name):
                return idea.name, idea.description, "fallback"

        raise AIServiceError("No unique AI or fallback project ideas are available")

    def generate_readme(self, name: str, description: str) -> str:
        """Generate README with fallback content."""

        try:
            return self._ai_service.generate_readme(
                name,
                description,
                self._settings.language,
            )
        except AIServiceError as exc:
            logger.warning("AI README generation failed; using fallback | error=%s", exc)
            return (
                f"# {name}\n\n"
                f"{description}\n\n"
                "## Setup\n\n"
                "Install dependencies and run the starter application.\n\n"
                "## Usage\n\n"
                "Start the service and call the health endpoint.\n"
            )

