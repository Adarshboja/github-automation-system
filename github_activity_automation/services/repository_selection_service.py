"""Repository filtering and random selection."""

from __future__ import annotations

import random

from github_activity_automation.config.settings import RepositoryFilters
from github_activity_automation.models.domain import RepositoryInfo


class RepositorySelectionService:
    """Select eligible repositories for commit automation."""

    def __init__(self, filters: RepositoryFilters) -> None:
        self._filters = filters

    def filter_repositories(self, repositories: list[RepositoryInfo]) -> list[RepositoryInfo]:
        """Apply configured repository filters."""

        return [repo for repo in repositories if self._is_allowed(repo)]

    def select_repository(
        self,
        repositories: list[RepositoryInfo],
        previous_repository: str | None,
        allow_previous: bool,
    ) -> RepositoryInfo | None:
        """Select a random eligible repository."""

        eligible = self.filter_repositories(repositories)
        if not allow_previous and previous_repository and len(eligible) > 1:
            eligible = [repo for repo in eligible if repo.full_name != previous_repository]
        if not eligible:
            return None
        return random.choice(eligible)

    def _is_allowed(self, repository: RepositoryInfo) -> bool:
        if self._filters.exclude_archived and repository.archived:
            return False
        if self._filters.exclude_forks and repository.fork:
            return False
        if repository.private and not self._filters.include_private:
            return False
        if not repository.private and not self._filters.include_public:
            return False
        if self._filters.name_allowlist and repository.name not in self._filters.name_allowlist:
            return False
        if repository.name in self._filters.name_blocklist:
            return False
        return True

