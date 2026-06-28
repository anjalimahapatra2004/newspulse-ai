from fastapi import APIRouter, Depends
from app.controllers import recommendation_controller
from app.utils.security import get_current_user_email

router = APIRouter(prefix="/api/recommendations", tags=["Recommendations"])


@router.get("/")
async def get_my_recommendations(limit: int = 20, user_email: str = Depends(get_current_user_email)):
    return await recommendation_controller.get_recommendations(user_email, limit)