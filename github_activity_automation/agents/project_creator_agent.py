"""Project creator automation agent."""

from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone

from github_activity_automation.config.settings import AppSettings
from github_activity_automation.github_client.client import GitHubClient
from github_activity_automation.repositories.project_repository import ProjectRepository
from github_activity_automation.repositories.state_repository import StateRepository
from github_activity_automation.services.project_generation_service import ProjectGenerationService
from github_activity_automation.services.project_template_service import ProjectTemplateService
from github_activity_automation.state.manager import StateManager
from github_activity_automation.utils.retry import with_retries

logger = logging.getLogger(__name__)


class ProjectCreatorAgent:
    """Create and seed new GitHub repositories."""

    AGENT_NAME = "project_creator_agent"

    def __init__(
        self,
        settings: AppSettings,
        github_client: GitHubClient,
        state_repository: StateRepository,
        project_repository: ProjectRepository,
        generation_service: ProjectGenerationService,
        template_service: ProjectTemplateService,
    ) -> None:
        self._settings = settings
        self._github_client = github_client
        self._state_repository = state_repository
        self._project_repository = project_repository
        self._generation_service = generation_service
        self._template_service = template_service
        self._state_manager = StateManager(state_repository, self.AGENT_NAME)

    def run(self) -> str:
        """Execute project creation."""

        if not self._settings.enabled:
            logger.info("Kill switch disabled automation; exiting project creator agent")
            return "disabled"

        run_id = str(uuid.uuid4())
        self._state_repository.start_execution(run_id, self.AGENT_NAME)
        try:
            self._github_client.validate_authentication()
            name, description, source = self._generation_service.generate_unique_project()
            self._project_repository.record_generated_name(name, description, source)
            readme = self._generation_service.generate_readme(name, description)
            content = self._template_service.build_content(name, description, readme)

            html_url = with_retries(
                lambda: self._github_client.create_repository(name, description),
                self._settings.runtime.retry_count,
                self._settings.runtime.retry_backoff_seconds,
                "create_repository",
            )
            full_name = f"{self._settings.github.username}/{name}"
            with_retries(
                lambda: self._github_client.seed_repository(
                    full_name,
                    {
                        "README.md": content.readme,
                        ".gitignore": content.gitignore,
                        "LICENSE": content.license_text,
                        content.starter_filename: content.starter_code,
                        content.requirements_filename: content.requirements_content,
                    },
                ),
                self._settings.runtime.retry_count,
                self._settings.runtime.retry_backoff_seconds,
                "seed_repository",
            )

            self._project_repository.record_created_repository(
                name=name,
                html_url=html_url,
                language=self._settings.project_creator.language,
                description=description,
            )
            self._state_manager.mark_successful_run()
            self._state_repository.finish_execution(
                run_id,
                "success",
                datetime.now(timezone.utc),
            )
            logger.info("Project creator agent completed | repository=%s", name)
            return "success"
        except Exception as exc:
            self._state_repository.finish_execution(
                run_id,
                "failed",
                datetime.now(timezone.utc),
                str(exc),
            )
            logger.exception("Project creator agent failed")
            raise

