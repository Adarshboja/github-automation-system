"""Typed runtime settings."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class RepositoryFilters:
    """Repository selection filters."""

    include_private: bool
    include_public: bool
    exclude_archived: bool
    exclude_forks: bool
    name_allowlist: list[str] = field(default_factory=list)
    name_blocklist: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class GitHubSettings:
    """GitHub integration settings."""

    token: str
    username: str
    timeout_seconds: int
    repository_filters: RepositoryFilters


@dataclass(frozen=True)
class DailyCommitSettings:
    """Daily commit agent settings."""

    tracking_filename: str
    min_commits: int
    max_commits: int
    commit_messages: list[str]
    force_allows_repeat_repository: bool


@dataclass(frozen=True)
class ProjectTemplateSettings:
    """Language template settings."""

    starter_filename: str
    requirements: list[str]


@dataclass(frozen=True)
class ProjectIdea:
    """Fallback project idea."""

    name: str
    description: str


@dataclass(frozen=True)
class ProjectCreatorSettings:
    """Project creator agent settings."""

    language: str
    default_license: str
    gitignore_template: str
    fallback_project_ideas: list[ProjectIdea]
    templates: dict[str, ProjectTemplateSettings]


@dataclass(frozen=True)
class AISettings:
    """AI provider settings."""

    provider: str
    model: str
    timeout_seconds: int
    gemini_url: str
    openrouter_url: str
    gemini_api_key: str
    openrouter_api_key: str


@dataclass(frozen=True)
class SchedulerSettings:
    """APScheduler settings."""

    timezone: str
    daily_commit_cron: str
    project_creator_cron: str


@dataclass(frozen=True)
class RuntimeSettings:
    """Runtime resilience settings."""

    retry_count: int
    retry_backoff_seconds: int


@dataclass(frozen=True)
class LoggingSettings:
    """Logging settings."""

    level: str
    directory: str
    filename: str
    max_bytes: int
    backup_count: int


@dataclass(frozen=True)
class DatabaseSettings:
    """Database settings."""

    url: str


@dataclass(frozen=True)
class AppSettings:
    """Top-level application settings."""

    enabled: bool
    database: DatabaseSettings
    github: GitHubSettings
    daily_commit: DailyCommitSettings
    project_creator: ProjectCreatorSettings
    ai: AISettings
    scheduler: SchedulerSettings
    runtime: RuntimeSettings
    logging: LoggingSettings

