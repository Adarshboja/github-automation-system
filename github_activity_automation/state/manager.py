"""State manager for agent execution state."""

from __future__ import annotations

from datetime import datetime, timezone

from github_activity_automation.repositories.state_repository import StateRepository


class StateManager:
    """High-level state operations."""

    LAST_SUCCESSFUL_RUN = "last_successful_run"
    LAST_REPOSITORY_COMMITTED = "last_repository_committed"

    def __init__(self, repository: StateRepository, agent_name: str) -> None:
        self._repository = repository
        self._agent_name = agent_name

    def get_last_repository_committed(self) -> str | None:
        return self._repository.get_value(
            self._agent_name,
            self.LAST_REPOSITORY_COMMITTED,
        )

    def get_last_successful_run(self) -> str | None:
        return self._repository.get_value(
            self._agent_name,
            self.LAST_SUCCESSFUL_RUN,
        )

    def set_last_repository_committed(self, repository_name: str) -> None:
        self._repository.set_value(
            self._agent_name,
            self.LAST_REPOSITORY_COMMITTED,
            repository_name,
        )

    def mark_successful_run(self) -> None:
        self._repository.set_value(
            self._agent_name,
            self.LAST_SUCCESSFUL_RUN,
            datetime.now(timezone.utc).isoformat(),
        )
