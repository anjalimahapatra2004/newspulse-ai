from bson import ObjectId
from bson.errors import InvalidId

from app.database import articles_collection, interactions_collection, users_collection
from app.models.interaction_model import InteractionModel
from app.exceptions import UserNotFoundError, AppError
from app.logger import get_logger

logger = get_logger(__name__)


def _serialize_article(doc: dict) -> dict:
    doc["id"] = str(doc.pop("_id"))
    doc.pop("embedding", None)  # don't ship raw vectors to the frontend
    return doc


async def get_articles(category: str | None, page: int, limit: int) -> list:
    try:
        query = {"category": category} if category else {}
        cursor = (
            articles_collection.find(query)
            .sort("published_at", -1)
            .skip((page - 1) * limit)
            .limit(limit)
        )
        return [_serialize_article(doc) async for doc in cursor]
    except Exception:
        logger.error("Failed to fetch articles (category=%s, page=%s)", category, page, exc_info=True)
        raise AppError("Couldn't load articles right now. Please try again.", status_code=500)


async def get_trending(limit: int = 10) -> list:
    """Cold-start fallback: most-interacted-with articles globally."""
    try:
        pipeline = [
            {"$group": {"_id": "$article_id", "score": {"$sum": "$weight"}}},
            {"$sort": {"score": -1}},
            {"$limit": limit},
        ]
        top = [row async for row in interactions_collection.aggregate(pipeline)]
        article_ids = [ObjectId(row["_id"]) for row in top]

        if not article_ids:
            cursor = articles_collection.find().sort("published_at", -1).limit(limit)
            return [_serialize_article(doc) async for doc in cursor]

        cursor = articles_collection.find({"_id": {"$in": article_ids}})
        return [_serialize_article(doc) async for doc in cursor]
    except Exception:
        logger.error("Failed to compute trending articles", exc_info=True)
        raise AppError("Couldn't load trending articles right now.", status_code=500)


async def log_interaction(user_email: str, article_id: str, action: str) -> dict:
    user = await users_collection.find_one({"email": user_email})
    if not user:
        logger.warning("Interaction logged for unknown user: %s", user_email)
        raise UserNotFoundError("We couldn't find your account. Please log in again.")

    try:
        interaction = InteractionModel(user_id=str(user["_id"]), article_id=article_id, action=action)
        await interactions_collection.insert_one(interaction.to_dict())
        logger.info("Interaction logged: user=%s article=%s action=%s", user_email, article_id, action)
        return {"message": "Interaction recorded."}
    except InvalidId:
        logger.warning("Invalid article_id in interaction: %s", article_id)
        raise AppError("That article reference looks invalid.", status_code=400)
    except Exception:
        logger.error("Failed to log interaction for %s", user_email, exc_info=True)
        raise AppError("Couldn't save that action right now.", status_code=500)