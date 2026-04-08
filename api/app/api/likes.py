from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.engine import Connection

from app.db.database import get_db
from app.schemas.like import LikeResponse
from app.services.auth_service import get_current_user_id
from app.services.like_service import LikeService

router = APIRouter()
like_service = LikeService()


@router.post("/api/articles/{article_id}/like", response_model=LikeResponse)
def like_article(
    article_id: int,
    db: Connection = Depends(get_db),
    current_user_id: str = Depends(get_current_user_id),
):
    result = like_service.like_article(db=db, article_id=article_id, user_id=current_user_id)
    if not result:
        raise HTTPException(status_code=404, detail="Article not found")
    return result


@router.delete("/api/articles/{article_id}/like", response_model=LikeResponse)
def unlike_article(
    article_id: int,
    db: Connection = Depends(get_db),
    current_user_id: str = Depends(get_current_user_id),
):
    result = like_service.unlike_article(db=db, article_id=article_id, user_id=current_user_id)
    if not result:
        raise HTTPException(status_code=404, detail="Article not found")
    return result


@router.get("/api/articles/{article_id}/like-status", response_model=LikeResponse)
def like_status(
    article_id: int,
    db: Connection = Depends(get_db),
    current_user_id: str = Depends(get_current_user_id),
):
    result = like_service.get_like_status(db=db, article_id=article_id, user_id=current_user_id)
    if not result:
        raise HTTPException(status_code=404, detail="Article not found")
    return result
