import json
from groq import Groq
from app.config import settings
from app.exceptions import ExternalServiceError
from app.logger import get_logger

logger = get_logger(__name__)

_client = Groq(api_key=settings.GROQ_API_KEY)
MODEL = "llama-3.1-8b-instant"


def tag_article(title: str, description: str) -> dict:
    """Zero-shot classification: returns category, tags, and a one-line AI summary."""
    prompt = f"""Classify this news article. Return ONLY valid JSON, no extra text.
Title: {title}
Description: {description}

Return JSON in this exact shape:
{{"category": "tech" or "world", "tags": ["tag1", "tag2"], "summary": "one line summary"}}
"""
    try:
        response = _client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
        )
        return json.loads(response.choices[0].message.content)
    except json.JSONDecodeError:
        logger.warning("Groq returned non-JSON for article tagging: %s", title)
        return {"category": "world", "tags": [], "summary": ""}
    except Exception:
        logger.error("Groq tagging request failed for article: %s", title, exc_info=True)
        raise ExternalServiceError("Article tagging is temporarily unavailable.")


def explain_recommendation(article_title: str, user_recent_titles: list) -> str:
    """Generates a short 'why this was recommended' line for the dashboard."""
    recent = ", ".join(user_recent_titles[:3]) if user_recent_titles else "your reading history"
    prompt = (
        f"In under 12 words, explain why someone who recently read about "
        f"'{recent}' might be interested in this article: '{article_title}'. "
        f"Reply with only the explanation, starting with 'Because'."
    )
    try:
        response = _client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
        )
        return response.choices[0].message.content.strip()
    except Exception:
        # Explanation text is a nice-to-have - fail quietly rather than breaking the feed
        logger.warning("Groq explanation request failed for article: %s", article_title, exc_info=True)
        return ""