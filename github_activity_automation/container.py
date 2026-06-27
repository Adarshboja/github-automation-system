"""Dependency assembly."""

from __future__ import annotations

from sqlalchemy.orm import Session

from github_activity_automation.agents.daily_commit_agent import DailyCommitAgent
from github_activity_automation.agents.project_creator_agent import ProjectCreatorAgent
from github_activity_automation.config.settings import AppSettings
from github_activity_automation.github_client.client import GitHubClient
from github_activity_automation.repositories.commit_repository import CommitRepository
from github_activity_automation.repositories.project_repository import ProjectRepository
from github_activity_automation.repositories.state_repository import StateRepository
from github_activity_automation.services.ai_service import AIService
from github_activity_automation.services.commit_service import CommitContentService
from github_activity_automation.services.project_generation_service import ProjectGenerationService
from github_activity_automation.services.project_template_service import ProjectTemplateService
from github_activity_automation.services.repository_selection_service import RepositorySelectionService


class Container:
    """Simple dependency container for a single database session."""

    def __init__(self, settings: AppSettings, session: Session) -> None:
        self.settings = settings
        self.session = session
        self.github_client = GitHubClient(settings.github)
        self.state_repository = StateRepository(session)
        self.commit_repository = CommitRepository(session)
        self.project_repository = ProjectRepository(session)
        self.ai_service = AIService(settings.ai)

    def daily_commit_agent(self) -> DailyCommitAgent:
        return DailyCommitAgent(
            settings=self.settings,
            github_client=self.github_client,
            state_repository=self.state_repository,
            commit_repository=self.commit_repository,
            selection_service=RepositorySelectionService(
                self.settings.github.repository_filters
            ),
            content_service=CommitContentService(),
        )

    def project_creator_agent(self) -> ProjectCreatorAgent:
        generation_service = ProjectGenerationService(
            self.settings.project_creator,
            self.ai_service,
            self.project_repository,
        )
        return ProjectCreatorAgent(
            settings=self.settings,
            github_client=self.github_client,
            state_repository=self.state_repository,
            project_repository=self.project_repository,
            generation_service=generation_service,
            template_service=ProjectTemplateService(self.settings.project_creator),
        )

