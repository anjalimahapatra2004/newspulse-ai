"""
News ingestion job for NewsPulse AI.

Pulls top headlines from NewsAPI (tech + world), skips anything already
stored (by URL), tags each article with Groq (category/tags/summary), and
generates a Sentence-Transformers embedding before saving to MongoDB.

Run from the backend/ folder (with your venv active):
    python -m scripts.ingest_news
"""

import asyncio
from datetime import datetime
import requests

from app.database import articles_collection
from app.models.article_model import ArticleModel
from app.services.groq_service import tag_article
from app.services.embedding_service import generate_embedding
from app.exceptions import ExternalServiceError
from app.config import settings
from app.logger import get_logger

logger = get_logger(__name__)

NEWS_API_URL = "https://newsapi.org/v2/top-headlines"
# NewsAPI categories we pull from -> our internal category labels
CATEGORY_MAP = {"technology": "tech", "general": "world"}


def fetch_from_newsapi(category: str, page_size: int = 20) -> list:
    """Fetches raw articles for one category from NewsAPI. Returns [] on failure."""
    try:
        response = requests.get(
            NEWS_API_URL,
            params={
                "category": category,
                "language": "en",
                "pageSize": page_size,
                "apiKey": settings.NEWS_API_KEY,
            },
            timeout=10,
        )
        response.raise_for_status()
        return response.json().get("articles", [])
    except requests.RequestException:
        logger.error("NewsAPI request failed for category=%s", category, exc_info=True)
        return []


async def process_article(raw: dict, fallback_category: str) -> bool:
    """Tags, embeds, and inserts a single article. Returns True if inserted."""
    url = raw.get("url")
    title = raw.get("title")
    description = raw.get("description") or ""

    if not url or not title or title == "[Removed]":
        return False

    existing = await articles_collection.find_one({"url": url})
    if existing:
        return False  # already ingested

    # Groq tagging - falls back to NewsAPI's own category if Groq is unavailable
    try:
        tags_result = tag_article(title, description)
        category = tags_result.get("category") or fallback_category
        tags = tags_result.get("tags") or []
        ai_summary = tags_result.get("summary") or ""
    except ExternalServiceError:
        logger.warning("Falling back to NewsAPI category for: %s", title)
        category, tags, ai_summary = fallback_category, [], ""

    try:
        embedding = generate_embedding(f"{title}. {description}")
    except ExternalServiceError:
        logger.warning("Skipping embedding for '%s' - embedding service unavailable", title)
        embedding = []

    published_at_raw = raw.get("publishedAt")
    try:
        published_at = datetime.strptime(published_at_raw, "%Y-%m-%dT%H:%M:%SZ") if published_at_raw else None
    except ValueError:
        published_at = None

    article = ArticleModel(
        title=title,
        description=description,
        url=url,
        source=raw.get("source", {}).get("name", "Unknown"),
        image_url=raw.get("urlToImage"),
        category=category,
        tags=tags,
        embedding=embedding,
        ai_summary=ai_summary,
        published_at=published_at,
    )
    await articles_collection.insert_one(article.to_dict())
    return True


async def run_ingestion():
    if not settings.NEWS_API_KEY:
        logger.error("NEWS_API_KEY is missing in .env - get a free key at newsapi.org")
        return

    total_inserted = 0
    for news_api_category, internal_category in CATEGORY_MAP.items():
        raw_articles = fetch_from_newsapi(news_api_category)
        logger.info("Fetched %s raw articles for category=%s", len(raw_articles), internal_category)

        for raw in raw_articles:
            try:
                inserted = await process_article(raw, internal_category)
                if inserted:
                    total_inserted += 1
            except Exception:
                logger.error("Failed to process article: %s", raw.get("title"), exc_info=True)

    logger.info("Ingestion complete - %s new articles added", total_inserted)


if __name__ == "__main__":
    asyncio.run(run_ingestion())