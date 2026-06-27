"""Commit content generation."""

from __future__ import annotations

from datetime import datetime, timezone


class CommitContentService:
    """Build tracking file content."""

    def build_tracking_content(self, repository_full_name: str, sequence: int) -> str:
        timestamp = datetime.now(timezone.utc).isoformat()
        return (
            "# Activity Automation\n\n"
            f"- Repository: {repository_full_name}\n"
            f"- Sequence: {sequence}\n"
            f"- Updated at: {timestamp}\n"
        )

