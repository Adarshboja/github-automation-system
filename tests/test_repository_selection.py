"""Repository selection tests."""

from github_activity_automation.models.domain import RepositoryInfo
from github_activity_automation.services.repository_selection_service import RepositorySelectionService


def test_repository_selection_ignores_archived_forked_and_previous(settings):
    service = RepositorySelectionService(settings.github.repository_filters)
    repositories = [
        RepositoryInfo("archived", "octocat/archived", False, True, False),
        RepositoryInfo("forked", "octocat/forked", False, False, True),
        RepositoryInfo("previous", "octocat/previous", False, False, False),
        RepositoryInfo("next", "octocat/next", False, False, False),
    ]

    selected = service.select_repository(
        repositories,
        previous_repository="octocat/previous",
        allow_previous=False,
    )

    assert selected is not None
    assert selected.full_name == "octocat/next"

