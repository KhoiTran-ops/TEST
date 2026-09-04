"""Timezone-aware weekday scheduling with database-backed overlap guard."""
import logging
from apscheduler.schedulers.blocking import BlockingScheduler

from config import get_settings
from .orchestrator import PipelineOrchestrator


def run_scheduled(orchestrator: PipelineOrchestrator | None = None) -> None:
    settings = get_settings(); runner = orchestrator or PipelineOrchestrator()
    scheduler = BlockingScheduler(timezone=settings.timezone)
    days = ",".join(day[:3] for day in settings.weekdays)
    scheduler.add_job(runner.run, "cron", day_of_week=days, hour=settings.schedule_hour,
                      minute=settings.schedule_minute, id="daily_pipeline", max_instances=1,
                      coalesce=True, misfire_grace_time=3600)
    logging.getLogger("pipeline").info("Scheduler ready: %s %02d:%02d", days, settings.schedule_hour, settings.schedule_minute)
    scheduler.start()
