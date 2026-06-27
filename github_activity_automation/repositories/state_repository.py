"""Persistence access for agent state and execution history."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from github_activity_automation.database.models import AgentExecutionHistory, AgentState


class StateRepository:
    """Repository for agent state."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def get_value(self, agent_name: str, key: str) -> str | None:
        statement = select(AgentState).where(
            AgentState.agent_name == agent_name,
            AgentState.key == key,
        )
        state = self._session.scalar(statement)
        return state.value if state else None

    def set_value(self, agent_name: str, key: str, value: str) -> None:
        statement = select(AgentState).where(
            AgentState.agent_name == agent_name,
            AgentState.key == key,
        )
        state = self._session.scalar(statement)
        if state:
            state.value = value
        else:
            self._session.add(AgentState(agent_name=agent_name, key=key, value=value))

    def start_execution(self, run_id: str, agent_name: str) -> None:
        self._session.add(
            AgentExecutionHistory(
                run_id=run_id,
                agent_name=agent_name,
                status="running",
            )
        )

    def finish_execution(
        self,
        run_id: str,
        status: str,
        finished_at: datetime,
        error_message: str | None = None,
    ) -> None:
        statement = select(AgentExecutionHistory).where(
            AgentExecutionHistory.run_id == run_id
        )
        execution = self._session.scalar(statement)
        if execution:
            execution.status = status
            execution.finished_at = finished_at
            execution.error_message = error_message

