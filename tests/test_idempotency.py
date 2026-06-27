"""Idempotency tests."""

from unittest.mock import Mock

from github_activity_automation.agents.daily_commit_agent import DailyCommitAgent
from github_activity_automation.models.domain import CommitResult, RepositoryInfo
from github_activity_automation.repositories.commit_repository import CommitRepository
from github_activity_automation.repositories.state_repository import StateRepository
from github_activity_automation.services.commit_service import CommitContentService
from github_activity_automation.services.repository_selection_service import RepositorySelectionService


def test_daily_commit_records_single_commit_per_configured_run(settings, session):
    github_client = Mock()
    github_client.list_repositories.return_value = [
        RepositoryInfo("repo", "octocat/repo", False, False, False)
    ]
    github_client.upsert_file_commit.return_value = CommitResult(
        sha="abc123",
        message="chore: test",
    )
    commit_repository = CommitRepository(session)
    agent = DailyCommitAgent(
        settings=settings,
        github_client=github_client,
        state_repository=StateRepository(session),
        commit_repository=commit_repository,
        selection_service=RepositorySelectionService(settings.github.repository_filters),
        content_service=CommitContentService(),
    )

    assert agent.run() == "success"
    assert github_client.upsert_file_commit.call_count == 1

