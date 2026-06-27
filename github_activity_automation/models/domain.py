"""Domain dataclasses shared across layers."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RepositoryInfo:
    """GitHub repository metadata used by the agents."""

    name: str
    full_name: str
    private: bool
    archived: bool
    fork: bool


@dataclass(frozen=True)
class CommitResult:
    """Result of a created commit."""

    sha: str
    message: str


@dataclass(frozen=True)
class ProjectContent:
    """Generated repository seed content."""

    readme: str
    gitignore: str
    license_text: str
    starter_filename: str
    starter_code: str
    requirements_filename: str
    requirements_content: str


@dataclass(frozen=True)
class ProjectPlan:
    """Project creation plan."""

    name: str
    description: str
    language: str
    content: ProjectContent
    source: str

