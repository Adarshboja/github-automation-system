"""Daily commit automation agent."""

from __future__ import annotations

import logging
import random
import uuid
from datetime import datetime, timezone

from github_activity_automation.config.settings import AppSettings
from github_activity_automation.github_client.client import GitHubClient
from github_activity_automation.repositories.commit_repository import CommitRepository
from github_activity_automation.repositories.state_repository import StateRepository
from github_activity_automation.services.commit_service import CommitContentService
from github_activity_automation.services.repository_selection_service import RepositorySelectionService
from github_activity_automation.state.manager import StateManager
from github_activity_automation.utils.retry import with_retries

logger = logging.getLogger(__name__)


class DailyCommitAgent:
    """Create small tracking commits across eligible repositories."""

    AGENT_NAME = "daily_commit_agent"

    def __init__(
        self,
        settings: AppSettings,
        github_client: GitHubClient,
        state_repository: StateRepository,
        commit_repository: CommitRepository,
        selection_service: RepositorySelectionService,
        content_service: CommitContentService,
    ) -> None:
        self._settings = settings
        self._github_client = github_client
        self._state_repository = state_repository
        self._commit_repository = commit_repository
        self._state_manager = StateManager(state_repository, self.AGENT_NAME)
        self._selection_service = selection_service
        self._content_service = content_service

    def run(self, force: bool = False) -> str:
        """Execute the daily commit agent."""

        if not self._settings.enabled:
            logger.info("Kill switch disabled automation; exiting daily commit agent")
            return "disabled"

        run_id = str(uuid.uuid4())
        self._state_repository.start_execution(run_id, self.AGENT_NAME)
        try:
            if self._already_ran_today() and not force:
                logger.info("Daily commit agent already completed today")
                self._state_repository.finish_execution(
                    run_id,
                    "skipped",
                    datetime.now(timezone.utc),
                    "Already completed today",
                )
                return "already_completed"
            self._github_client.validate_authentication()
            repositories = with_retries(
                self._github_client.list_repositories,
                self._settings.runtime.retry_count,
                self._settings.runtime.retry_backoff_seconds,
                "list_repositories",
            )
            previous_repository = self._state_manager.get_last_repository_committed()
            selected = self._selection_service.select_repository(
                repositories=repositories,
                previous_repository=previous_repository,
                allow_previous=force and self._settings.daily_commit.force_allows_repeat_repository,
            )
            if selected is None:
                logger.warning("No eligible repositories found")
                return "no_repository"

            commit_count = random.randint(
                self._settings.daily_commit.min_commits,
                self._settings.daily_commit.max_commits,
            )
            for sequence in range(1, commit_count + 1):
                message = random.choice(self._settings.daily_commit.commit_messages)
                content = self._content_service.build_tracking_content(
                    selected.full_name,
                    sequence,
                )
                result = with_retries(
                    lambda: self._github_client.upsert_file_commit(
                        repository_full_name=selected.full_name,
                        path=self._settings.daily_commit.tracking_filename,
                        content=content,
                        message=message,
                    ),
                    self._settings.runtime.retry_count,
                    self._settings.runtime.retry_backoff_seconds,
                    "upsert_file_commit",
                )
                self._commit_repository.add_commit(
                    repository_name=selected.full_name,
                    commit_sha=result.sha,
                    message=result.message,
                    run_id=run_id,
                )

            self._state_manager.set_last_repository_committed(selected.full_name)
            self._state_manager.mark_successful_run()
            self._state_repository.finish_execution(
                run_id,
                "success",
                datetime.now(timezone.utc),
            )
            logger.info("Daily commit agent completed | repository=%s", selected.full_name)
            return "success"
        except Exception as exc:
            self._state_repository.finish_execution(
                run_id,
                "failed",
                datetime.now(timezone.utc),
                str(exc),
            )
            logger.exception("Daily commit agent failed")
            raise

    def _already_ran_today(self) -> bool:
        last_run = self._state_manager.get_last_successful_run()
        if not last_run:
            return False
        try:
            last_run_date = datetime.fromisoformat(last_run).date()
        except ValueError:
            return False
        return last_run_date == datetime.now(timezone.utc).date()
