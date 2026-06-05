"""Background jobs — alert generation and optional OEM portal sync."""

import logging

from apscheduler.schedulers.background import BackgroundScheduler

from app.core.config import settings
from app.db.session import SessionLocal

logger = logging.getLogger(__name__)
scheduler = BackgroundScheduler()


def _run_alert_job() -> None:
    from app.services.ai_alerts import generate_alerts

    db = SessionLocal()
    try:
        count = len(generate_alerts(db, clear_existing=True))
        logger.info("Alert job completed: %s new alerts", count)
    except Exception:
        logger.exception("Alert job failed")
    finally:
        db.close()


def _run_portal_sync_job() -> None:
    from app.services.integrations.sync import any_portal_configured, sync_all_portals

    if not any_portal_configured():
        logger.debug("Portal sync skipped — no APIs configured")
        return

    db = SessionLocal()
    try:
        results = sync_all_portals(db, source="scheduled")
        db.commit()
        logger.info("Portal sync completed: %s", results)
    except Exception:
        logger.exception("Portal sync failed")
        db.rollback()
    finally:
        db.close()


def start_scheduler() -> None:
    if not settings.SCHEDULER_ENABLED:
        return
    if scheduler.running:
        return

    scheduler.add_job(
        _run_alert_job,
        "interval",
        minutes=settings.ALERT_JOB_INTERVAL_MINUTES,
        id="alerts",
        replace_existing=True,
        max_instances=1,
        coalesce=True,
    )

    if settings.PORTAL_AUTO_SYNC:
        scheduler.add_job(
            _run_portal_sync_job,
            "interval",
            minutes=settings.PORTAL_SYNC_INTERVAL_MINUTES,
            id="portal_sync",
            replace_existing=True,
            max_instances=1,
            coalesce=True,
        )
        logger.info("Portal auto-sync every %s min", settings.PORTAL_SYNC_INTERVAL_MINUTES)
    else:
        logger.info("Portal auto-sync disabled (set PORTAL_AUTO_SYNC=true when APIs are ready)")

    scheduler.start()
    logger.info("Background scheduler started")


def stop_scheduler() -> None:
    if scheduler.running:
        scheduler.shutdown(wait=False)
