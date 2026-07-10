"""Background scheduling: auto-start/end, reminders, milestones, recurrence.

Uses python-telegram-bot's built-in JobQueue (APScheduler under the hood) so
it shares the bot's event loop. A single periodic "tick" reconciles giveaway
state; this is robust to restarts because state lives in the database.
"""
from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone

from telegram.ext import Application, ContextTypes

from .database import session_scope
from .database.enums import GiveawayStatus, GiveawayType
from .services import (
    giveaway_service,
    notification_service,
    winner_service,
)

logger = logging.getLogger(__name__)

# Milestone thresholds that trigger a public announcement
_MILESTONES = [10, 25, 50, 100, 250, 500, 1000, 5000, 10000]


async def tick(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Periodic reconciliation of giveaway lifecycle."""
    bot = context.bot
    now = datetime.now(timezone.utc)
    with session_scope() as session:
        # 1) Auto-start scheduled giveaways whose start time has arrived
        scheduled = giveaway_service.list_giveaways(session, [GiveawayStatus.SCHEDULED])
        for g in scheduled:
            if g.start_at and g.start_at <= now:
                giveaway_service.start_giveaway(session, g.id)
                await notification_service.announce_start(bot, session, g)
                logger.info("Auto-started giveaway #%s", g.id)

        # 2) Auto-end active giveaways past their end time
        active = giveaway_service.list_giveaways(session, [GiveawayStatus.ACTIVE])
        for g in active:
            # milestone announcements
            await _maybe_announce_milestone(session, bot, g)

            # reminder ~1h before end (once)
            if g.end_at:
                delta = g.end_at - now
                if timedelta(minutes=55) <= delta <= timedelta(minutes=65):
                    marker = f"reminded"
                    if (g.milestones_announced or "").find(marker) == -1:
                        await notification_service.send_reminder(bot, session, g)
                        g.milestones_announced = (g.milestones_announced or "") + f"|{marker}"

            if g.end_at and g.end_at <= now:
                giveaway_service.end_giveaway(session, g.id)
                await notification_service.announce_end(bot, g)
                # draw winners (skip pure instant-win giveaways)
                if g.type != GiveawayType.INSTANT:
                    winners = winner_service.select_winners(session, g)
                    await notification_service.notify_winners(bot, session, g, winners)
                logger.info("Auto-ended giveaway #%s", g.id)

                # recurrence
                if g.is_recurring:
                    giveaway_service.clone_for_recurrence(session, g)


async def _maybe_announce_milestone(session, bot, giveaway) -> None:
    count = giveaway_service.count_participants(session, giveaway.id)
    announced = set(
        int(x) for x in (giveaway.milestones_announced or "").split(",") if x.strip().isdigit()
    )
    for m in _MILESTONES:
        if count >= m and m not in announced:
            await notification_service.announce_milestone(bot, giveaway, count)
            announced.add(m)
    giveaway.milestones_announced = ",".join(str(x) for x in sorted(announced))


def register_jobs(application: Application) -> None:
    """Attach periodic jobs to the application's job queue."""
    job_queue = application.job_queue
    if job_queue is None:
        logger.warning(
            "JobQueue not available. Install python-telegram-bot[job-queue] "
            "to enable scheduling."
        )
        return
    # run every 60 seconds, first run after 10s
    job_queue.run_repeating(tick, interval=60, first=10, name="giveaway_tick")
    logger.info("Scheduler jobs registered (tick every 60s).")
