from fastapi import APIRouter, Depends, Query
from app.controllers import article_controller
from app.schemas.article_schema import InteractionSchema
from app.utils.security import get_current_user_email

router = APIRouter(prefix="/api/articles", tags=["Articles"])


@router.get("/")
async def list_articles(category: str | None = None, page: int = 1, limit: int = 20):
    return await article_controller.get_articles(category, page, limit)


@router.get("/trending")
async def trending(limit: int = 10):
    return await article_controller.get_trending(limit)


@router.post("/interactions")
async def log_interaction(data: InteractionSchema, user_email: str = Depends(get_current_user_email)):
    return await article_controller.log_interaction(user_email, data.article_id, data.action)