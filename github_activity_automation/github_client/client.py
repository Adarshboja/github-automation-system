"""PyGithub adapter."""

from __future__ import annotations

import logging

from github import Github, GithubException, RateLimitExceededException

from github_activity_automation.config.settings import GitHubSettings
from github_activity_automation.exceptions import GitHubClientError
from github_activity_automation.models.domain import CommitResult, RepositoryInfo

logger = logging.getLogger(__name__)


class GitHubClient:
    """Thin adapter around PyGithub."""

    def __init__(self, settings: GitHubSettings) -> None:
        self._settings = settings
        self._github = Github(
            login_or_token=settings.token,
            timeout=settings.timeout_seconds,
        )

    def validate_authentication(self) -> None:
        """Validate token and configured user."""

        try:
            user = self._github.get_user()
            login = user.login
        except GithubException as exc:
            raise GitHubClientError("GitHub authentication failed") from exc
        if self._settings.username and login.lower() != self._settings.username.lower():
            logger.warning("Authenticated as %s, configured username is %s", login, self._settings.username)

    def list_repositories(self) -> list[RepositoryInfo]:
        """Fetch repositories for the authenticated user."""

        try:
            repositories = self._github.get_user().get_repos()
            return [
                RepositoryInfo(
                    name=repo.name,
                    full_name=repo.full_name,
                    private=repo.private,
                    archived=repo.archived,
                    fork=repo.fork,
                )
                for repo in repositories
            ]
        except RateLimitExceededException as exc:
            raise GitHubClientError("GitHub rate limit exceeded") from exc
        except GithubException as exc:
            raise GitHubClientError("Failed to fetch repositories") from exc

    def upsert_file_commit(
        self,
        repository_full_name: str,
        path: str,
        content: str,
        message: str,
    ) -> CommitResult:
        """Create or update a file in a repository."""

        try:
            repo = self._github.get_repo(repository_full_name)
            try:
                existing = repo.get_contents(path)
                result = repo.update_file(
                    path=path,
                    message=message,
                    content=content,
                    sha=existing.sha,
                )
            except GithubException as exc:
                if exc.status != 404:
                    raise
                result = repo.create_file(path=path, message=message, content=content)
            sha = result["commit"].sha
            return CommitResult(sha=sha, message=message)
        except RateLimitExceededException as exc:
            raise GitHubClientError("GitHub rate limit exceeded") from exc
        except GithubException as exc:
            raise GitHubClientError(f"Failed to commit to {repository_full_name}") from exc

    def create_repository(
        self,
        name: str,
        description: str,
        private: bool = False,
    ) -> str:
        """Create a GitHub repository and return its URL."""

        try:
            repo = self._github.get_user().create_repo(
                name=name,
                description=description,
                private=private,
                auto_init=False,
            )
            return repo.html_url
        except RateLimitExceededException as exc:
            raise GitHubClientError("GitHub rate limit exceeded") from exc
        except GithubException as exc:
            raise GitHubClientError(f"Failed to create repository {name}") from exc

    def seed_repository(
        self,
        repository_full_name: str,
        files: dict[str, str],
    ) -> None:
        """Seed a repository with initial files."""

        for path, content in files.items():
            self.upsert_file_commit(
                repository_full_name=repository_full_name,
                path=path,
                content=content,
                message=f"chore: add {path}",
            )
