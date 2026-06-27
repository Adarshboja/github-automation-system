"""Command-line entry point."""

from __future__ import annotations

import argparse
import logging

from github_activity_automation.config.loader import load_settings
from github_activity_automation.container import Container
from github_activity_automation.database.session import create_session_factory, session_scope
from github_activity_automation.logging_config import configure_logging

logger = logging.getLogger(__name__)


def parse_args() -> argparse.Namespace:
    """Parse CLI arguments."""

    parser = argparse.ArgumentParser(description="GitHub Activity Automation System")
    parser.add_argument(
        "agent",
        choices=["daily-commit", "project-creator"],
        help="Agent to run",
    )
    parser.add_argument("--config", default="config.yaml", help="Path to config.yaml")
    parser.add_argument(
        "--force",
        action="store_true",
        help="Allow daily commit agent to reuse the previous repository",
    )
    return parser.parse_args()


def main() -> None:
    """Run a selected automation agent."""

    args = parse_args()
    settings = load_settings(args.config)
    configure_logging(settings.logging)
    if not settings.enabled:
        logger.info("Kill switch is disabled; exiting without GitHub API calls")
        return

    session_factory = create_session_factory(settings.database.url)
    with session_scope(session_factory) as session:
        container = Container(settings, session)
        if args.agent == "daily-commit":
            result = container.daily_commit_agent().run(force=args.force)
        else:
            result = container.project_creator_agent().run()
        logger.info("Agent finished | agent=%s | result=%s", args.agent, result)


if __name__ == "__main__":
    main()
