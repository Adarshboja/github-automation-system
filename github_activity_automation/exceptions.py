"""Application-specific exceptions."""


class AutomationError(Exception):
    """Base exception for automation failures."""


class ConfigurationError(AutomationError):
    """Raised when configuration is invalid."""


class GitHubClientError(AutomationError):
    """Raised when GitHub operations fail."""


class AIServiceError(AutomationError):
    """Raised when AI generation fails."""


class DatabaseError(AutomationError):
    """Raised when persistence fails."""

