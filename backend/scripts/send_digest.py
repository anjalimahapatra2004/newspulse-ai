"""
Digest email job for NewsPulse AI.

For every user, builds a personalized Tech/AI + World digest (using the same
hybrid recommendation engine as the dashboard) and emails it to their
registered address. Falls back to trending articles if a user has no
reading history yet.

Run from the backend/ folder (with your venv active):
    python -m scripts.send_digest

In production you'd schedule this with Windows Task Scheduler / cron to run
once a day (e.g. every morning) - see backend/README.md for the command.
"""

import asyncio

from app.database import users_collection
from app.controllers.recommendation_controller import get_recommendations
from app.services.email_service import send_digest_email
from app.exceptions import EmailDeliveryError
from app.logger import get_logger

logger = get_logger(__name__)

ARTICLES_PER_CATEGORY = 5


async def build_digest_for_user(user: dict) -> tuple[list, list]:
    """Returns (tech_articles, world_articles) respecting the user's preferences."""
    preferences = user.get("preferences", ["tech", "world"])
    recommendations = await get_recommendations(user["email"], limit=30)

    tech_articles = [a for a in recommendations if a.get("category") == "tech"][:ARTICLES_PER_CATEGORY] \
        if "tech" in preferences else []
    world_articles = [a for a in recommendations if a.get("category") == "world"][:ARTICLES_PER_CATEGORY] \
        if "world" in preferences else []

    return tech_articles, world_articles


async def run_digest():
    users = [u async for u in users_collection.find({})]
    logger.info("Building digests for %s users", len(users))

    sent_count = 0
    for user in users:
        try:
            tech_articles, world_articles = await build_digest_for_user(user)
            if not tech_articles and not world_articles:
                logger.info("Skipping %s - no articles match their preferences yet", user["email"])
                continue

            await send_digest_email(user["email"], user["name"], tech_articles, world_articles)
            sent_count += 1
        except EmailDeliveryError:
            logger.error("Digest email failed to send for %s", user["email"])
        except Exception:
            logger.error("Unexpected error building digest for %s", user["email"], exc_info=True)

    logger.info("Digest run complete - sent to %s/%s users", sent_count, len(users))


if __name__ == "__main__":
    asyncio.run(run_digest())