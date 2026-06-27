"""APScheduler wiring."""

from __future__ import annotations

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from github_activity_automation.agents.daily_commit_agent import DailyCommitAgent
from github_activity_automation.agents.project_creator_agent import ProjectCreatorAgent
from github_activity_automation.config.settings import AppSettings
from github_activity_automation.repositories.scheduling_repository import SchedulingRepository


def build_scheduler(
    settings: AppSettings,
    daily_commit_agent: DailyCommitAgent,
    project_creator_agent: ProjectCreatorAgent,
    scheduling_repository: SchedulingRepository,
) -> BackgroundScheduler:
    """Create and configure APScheduler jobs."""

    scheduler = BackgroundScheduler(timezone=settings.scheduler.timezone)
    scheduling_repository.upsert_job(
        "daily_commit_agent",
        settings.scheduler.daily_commit_cron,
        settings.scheduler.timezone,
        settings.enabled,
    )
    scheduling_repository.upsert_job(
        "project_creator_agent",
        settings.scheduler.project_creator_cron,
        settings.scheduler.timezone,
        settings.enabled,
    )
    if settings.enabled:
        scheduler.add_job(
            daily_commit_agent.run,
            CronTrigger.from_crontab(settings.scheduler.daily_commit_cron),
            id="daily_commit_agent",
            replace_existing=True,
        )
        scheduler.add_job(
            project_creator_agent.run,
            CronTrigger.from_crontab(settings.scheduler.project_creator_cron),
            id="project_creator_agent",
            replace_existing=True,
        )
    return scheduler

