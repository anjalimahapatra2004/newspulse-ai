from datetime import datetime, timezone
from typing import Optional


class ArticleModel:
    """Represents a news article document, including its embedding and AI tags."""

    def __init__(
        self,
        title: str,
        description: str,
        url: str,
        source: str,
        image_url: Optional[str] = None,
        category: Optional[str] = None,
        tags: Optional[list] = None,
        embedding: Optional[list] = None,
        ai_summary: Optional[str] = None,
        published_at: Optional[datetime] = None,
        created_at: Optional[datetime] = None,
    ):
        self.title = title
        self.description = description
        self.url = url
        self.source = source
        self.image_url = image_url
        # "tech" or "world" (drives notification + dashboard filtering)
        self.category = category or "world"
        self.tags = tags or []
        self.embedding = embedding or []
        self.ai_summary = ai_summary
        self.published_at = published_at or datetime.now(timezone.utc)
        self.created_at = created_at or datetime.now(timezone.utc)

    def to_dict(self) -> dict:
        return {
            "title": self.title,
            "description": self.description,
            "url": self.url,
            "source": self.source,
            "image_url": self.image_url,
            "category": self.category,
            "tags": self.tags,
            "embedding": self.embedding,
            "ai_summary": self.ai_summary,
            "published_at": self.published_at,
            "created_at": self.created_at,
        }