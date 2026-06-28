from datetime import datetime, timezone
import numpy as np
from bson import ObjectId

from app.database import articles_collection, interactions_collection, users_collection
from app.services.embedding_service import cosine_similarity
from app.controllers.article_controller import get_trending, _serialize_article
from app.exceptions import AppError
from app.logger import get_logger

logger = get_logger(__name__)

# Tunable hybrid weights: final_score = α·content + β·collaborative + γ·recency
ALPHA, BETA, GAMMA = 0.5, 0.3, 0.2


async def _user_profile_vector(user_id: str) -> list:
    """Average embedding of articles the user has engaged with most recently."""
    cursor = interactions_collection.find({"user_id": user_id}).sort("created_at", -1).limit(20)
    article_ids = [ObjectId(row["article_id"]) async for row in cursor]
    if not article_ids:
        return []

    articles = articles_collection.find({"_id": {"$in": article_ids}})
    vectors = [doc["embedding"] async for doc in articles if doc.get("embedding")]
    if not vectors:
        return []
    return np.mean(np.array(vectors), axis=0).tolist()


async def _collaborative_scores(user_id: str) -> dict:
    """Lightweight matrix factorization over the user-article interaction matrix."""
    from sklearn.decomposition import TruncatedSVD  # imported lazily - see note in embedding_service.py

    rows = [row async for row in interactions_collection.find({}, {"user_id": 1, "article_id": 1, "weight": 1})]
    if len(rows) < 10:
        logger.info("Skipping collaborative scoring - not enough interaction data yet (%s rows)", len(rows))
        return {}

    try:
        user_ids = sorted({r["user_id"] for r in rows})
        article_ids = sorted({r["article_id"] for r in rows})
        user_idx = {u: i for i, u in enumerate(user_ids)}
        article_idx = {a: i for i, a in enumerate(article_ids)}

        matrix = np.zeros((len(user_ids), len(article_ids)))
        for r in rows:
            matrix[user_idx[r["user_id"]], article_idx[r["article_id"]]] += r["weight"]

        n_components = min(10, min(matrix.shape) - 1) or 1
        svd = TruncatedSVD(n_components=n_components, random_state=42)
        user_factors = svd.fit_transform(matrix)
        article_factors = svd.components_.T

        if user_id not in user_idx:
            return {}
        predicted = user_factors[user_idx[user_id]] @ article_factors.T
        return {aid: float(predicted[idx]) for aid, idx in article_idx.items()}
    except Exception:
        # Collaborative scoring is an enhancement, not critical path - degrade gracefully
        logger.error("Collaborative scoring failed, falling back to content + recency only", exc_info=True)
        return {}


def _recency_boost(published_at: datetime) -> float:
    if published_at.tzinfo is None:
        published_at = published_at.replace(tzinfo=timezone.utc)
    hours_old = (datetime.now(timezone.utc) - published_at).total_seconds() / 3600
    return max(0.0, 1 - (hours_old / 72))  # decays to 0 over 3 days


async def get_recommendations(user_email: str, limit: int = 20) -> list:
    user = await users_collection.find_one({"email": user_email})
    if not user:
        logger.warning("Recommendation request for unknown user: %s", user_email)
        return []

    try:
        user_id = str(user["_id"])
        profile_vector = await _user_profile_vector(user_id)
        collaborative_scores = await _collaborative_scores(user_id)

        if not profile_vector:
            logger.info("Cold start for %s - serving trending feed", user_email)
            return await get_trending(limit)

        candidates = [
            doc async for doc in articles_collection.find({"category": {"$in": user.get("preferences", [])}})
        ]

        scored = []
        for doc in candidates:
            content_score = cosine_similarity(profile_vector, doc.get("embedding", []))
            collab_score = collaborative_scores.get(str(doc["_id"]), 0.0)
            recency_score = _recency_boost(doc["published_at"])
            final_score = (ALPHA * content_score) + (BETA * collab_score) + (GAMMA * recency_score)
            scored.append((final_score, doc))

        scored.sort(key=lambda x: x[0], reverse=True)
        top_scored = scored[:limit]

        if not top_scored:
            return []

        raw_scores = [s for s, _ in top_scored]
        lo, hi = min(raw_scores), max(raw_scores)
        spread = (hi - lo) or 1.0  # avoid divide-by-zero when all scores are equal

        results = []
        for score, doc in top_scored:
            normalized = (score - lo) / spread
            serialized = _serialize_article(dict(doc))
            serialized["score"] = round(normalized, 3)
            results.append(serialized)

        logger.info("Generated %s recommendations for %s", len(results), user_email)
        return results
    except Exception:
        logger.error("Failed to generate recommendations for %s", user_email, exc_info=True)
        raise AppError("Couldn't build your feed right now. Please refresh in a moment.", status_code=500)