"""Kill switch tests."""

from unittest.mock import Mock

from github_activity_automation.agents.daily_commit_agent import DailyCommitAgent
from github_activity_automation.repositories.commit_repository import CommitRepository
from github_activity_automation.repositories.state_repository import StateRepository
from github_activity_automation.services.commit_service import CommitContentService
from github_activity_automation.services.repository_selection_service import RepositorySelectionService


def test_kill_switch_exits_before_github_calls(settings, session):
    disabled_settings = settings.__class__(**{**settings.__dict__, "enabled": False})
    github_client = Mock()
    agent = DailyCommitAgent(
        settings=disabled_settings,
        github_client=github_client,
        state_repository=StateRepository(session),
        commit_repository=CommitRepository(session),
        selection_service=RepositorySelectionService(
            disabled_settings.github.repository_filters
        ),
        content_service=CommitContentService(),
    )

    assert agent.run() == "disabled"
    github_client.validate_authentication.assert_not_called()

