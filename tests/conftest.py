"""Shared test fixtures."""

from __future__ import annotations

import pytest
from sqlalchemy.orm import Session

from github_activity_automation.config.settings import (
    AISettings,
    AppSettings,
    DailyCommitSettings,
    DatabaseSettings,
    GitHubSettings,
    LoggingSettings,
    ProjectCreatorSettings,
    ProjectIdea,
    ProjectTemplateSettings,
    RepositoryFilters,
    RuntimeSettings,
    SchedulerSettings,
)
from github_activity_automation.database.session import create_session_factory


@pytest.fixture()
def settings() -> AppSettings:
    return AppSettings(
        enabled=True,
        database=DatabaseSettings(url="sqlite:///:memory:"),
        github=GitHubSettings(
            token="token",
            username="octocat",
            timeout_seconds=10,
            repository_filters=RepositoryFilters(
                include_private=True,
                include_public=True,
                exclude_archived=True,
                exclude_forks=True,
                name_allowlist=[],
                name_blocklist=[],
            ),
        ),
        daily_commit=DailyCommitSettings(
            tracking_filename=".activity.md",
            min_commits=1,
            max_commits=1,
            commit_messages=["chore: test"],
            force_allows_repeat_repository=True,
        ),
        project_creator=ProjectCreatorSettings(
            language="python",
            default_license="MIT",
            gitignore_template="Python",
            fallback_project_ideas=[
                ProjectIdea("alpha-service", "Alpha service"),
                ProjectIdea("beta-service", "Beta service"),
            ],
            templates={
                "python": ProjectTemplateSettings(
                    starter_filename="main.py",
                    requirements=["fastapi"],
                )
            },
        ),
        ai=AISettings(
            provider="gemini",
            model="gemini-1.5-flash",
            timeout_seconds=10,
            gemini_url="https://example.com/{model}",
            openrouter_url="https://example.com",
            gemini_api_key="",
            openrouter_api_key="",
        ),
        scheduler=SchedulerSettings(
            timezone="UTC",
            daily_commit_cron="0 9 * * *",
            project_creator_cron="0 10 * * MON",
        ),
        runtime=RuntimeSettings(retry_count=1, retry_backoff_seconds=0),
        logging=LoggingSettings(
            level="INFO",
            directory="logs",
            filename="test.log",
            max_bytes=1024,
            backup_count=1,
        ),
    )


@pytest.fixture()
def session() -> Session:
    factory = create_session_factory("sqlite:///:memory:")
    db_session = factory()
    try:
        yield db_session
    finally:
        db_session.close()

