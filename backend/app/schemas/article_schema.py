from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class ArticleResponse(BaseModel):
    id: str
    title: str
    description: str
    url: str
    source: str
    image_url: Optional[str] = None
    category: str
    tags: List[str] = []
    ai_summary: Optional[str] = None
    published_at: datetime
    reason: Optional[str] = None  # "Because you read about LLMs"


class InteractionSchema(BaseModel):
    article_id: str
    action: str  # "click" | "like" | "read"