"""Configuration loading and validation."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import yaml
from dotenv import load_dotenv

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
from github_activity_automation.exceptions import ConfigurationError


def load_settings(config_path: str = "config.yaml") -> AppSettings:
    """Load settings from YAML and environment variables."""

    load_dotenv()
    path = Path(config_path)
    if not path.exists():
        raise ConfigurationError(f"Configuration file not found: {config_path}")

    with path.open("r", encoding="utf-8") as config_file:
        raw = yaml.safe_load(config_file) or {}

    try:
        settings = _build_settings(raw)
    except KeyError as exc:
        raise ConfigurationError(f"Missing configuration key: {exc}") from exc

    _validate_settings(settings)
    return settings


def _build_settings(raw: dict[str, Any]) -> AppSettings:
    github_raw = raw["github"]
    filters_raw = github_raw["repository_filters"]
    daily_raw = raw["daily_commit"]
    project_raw = raw["project_creator"]
    ai_raw = raw["ai"]
    scheduler_raw = raw["scheduler"]
    runtime_raw = raw["runtime"]
    logging_raw = raw["logging"]

    templates = {
        language: ProjectTemplateSettings(
            starter_filename=value["starter_filename"],
            requirements=list(value["requirements"]),
        )
        for language, value in project_raw["templates"].items()
    }

    fallback_ideas = [
        ProjectIdea(name=item["name"], description=item["description"])
        for item in project_raw["fallback_project_ideas"]
    ]

    return AppSettings(
        enabled=bool(raw["enabled"]),
        database=DatabaseSettings(url=raw["database"]["url"]),
        github=GitHubSettings(
            token=os.getenv("GITHUB_TOKEN", ""),
            username=os.getenv("GITHUB_USERNAME", github_raw.get("username", "")),
            timeout_seconds=int(github_raw["timeout_seconds"]),
            repository_filters=RepositoryFilters(
                include_private=bool(filters_raw["include_private"]),
                include_public=bool(filters_raw["include_public"]),
                exclude_archived=bool(filters_raw["exclude_archived"]),
                exclude_forks=bool(filters_raw["exclude_forks"]),
                name_allowlist=list(filters_raw["name_allowlist"]),
                name_blocklist=list(filters_raw["name_blocklist"]),
            ),
        ),
        daily_commit=DailyCommitSettings(
            tracking_filename=daily_raw["tracking_filename"],
            min_commits=int(daily_raw["min_commits"]),
            max_commits=int(daily_raw["max_commits"]),
            commit_messages=list(daily_raw["commit_messages"]),
            force_allows_repeat_repository=bool(
                daily_raw["force_allows_repeat_repository"]
            ),
        ),
        project_creator=ProjectCreatorSettings(
            language=project_raw["language"],
            default_license=project_raw["default_license"],
            gitignore_template=project_raw["gitignore_template"],
            fallback_project_ideas=fallback_ideas,
            templates=templates,
        ),
        ai=AISettings(
            provider=ai_raw["provider"],
            model=ai_raw["model"],
            timeout_seconds=int(ai_raw["timeout_seconds"]),
            gemini_url=ai_raw["gemini_url"],
            openrouter_url=ai_raw["openrouter_url"],
            gemini_api_key=os.getenv("GEMINI_API_KEY", ""),
            openrouter_api_key=os.getenv("OPENROUTER_API_KEY", ""),
        ),
        scheduler=SchedulerSettings(
            timezone=scheduler_raw["timezone"],
            daily_commit_cron=scheduler_raw["daily_commit_cron"],
            project_creator_cron=scheduler_raw["project_creator_cron"],
        ),
        runtime=RuntimeSettings(
            retry_count=int(runtime_raw["retry_count"]),
            retry_backoff_seconds=int(runtime_raw["retry_backoff_seconds"]),
        ),
        logging=LoggingSettings(
            level=logging_raw["level"],
            directory=logging_raw["directory"],
            filename=logging_raw["filename"],
            max_bytes=int(logging_raw["max_bytes"]),
            backup_count=int(logging_raw["backup_count"]),
        ),
    )


def _validate_settings(settings: AppSettings) -> None:
    if not settings.enabled:
        return
    if not settings.github.token:
        raise ConfigurationError("GITHUB_TOKEN is required when enabled is true")
    if not settings.github.username:
        raise ConfigurationError("GITHUB_USERNAME or github.username is required")
    if settings.daily_commit.min_commits < 1:
        raise ConfigurationError("daily_commit.min_commits must be at least 1")
    if settings.daily_commit.max_commits < settings.daily_commit.min_commits:
        raise ConfigurationError("daily_commit.max_commits must be >= min_commits")
    if not settings.daily_commit.commit_messages:
        raise ConfigurationError("daily_commit.commit_messages cannot be empty")
    language = settings.project_creator.language
    if language not in settings.project_creator.templates:
        raise ConfigurationError(f"No project template configured for {language}")
    if settings.runtime.retry_count < 1:
        raise ConfigurationError("runtime.retry_count must be at least 1")

