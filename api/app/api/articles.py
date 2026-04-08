from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.engine import Connection

from app.db.database import get_db
from app.schemas.article import ArticleDetail, ArticleFeedItem
from app.services.article_service import ArticleService
from app.services.auth_service import get_current_user_id

router = APIRouter()
article_service = ArticleService()


@router.get("/api/articles", response_model=list[ArticleFeedItem])
def get_articles(
    commodity_group: str | None = Query(default=None),
    commodity_classification: str | None = Query(default=None),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    db: Connection = Depends(get_db),
    current_user_id: str = Depends(get_current_user_id),
):
    return article_service.get_articles(
        db=db,
        current_user_id=current_user_id,
        commodity_group=commodity_group,
        commodity_classification=commodity_classification,
        skip=skip,
        limit=limit,
    )


@router.get("/api/articles/filters")
def get_filter_options(
    db: Connection = Depends(get_db),
    current_user_id: str = Depends(get_current_user_id),
):
    return article_service.get_filter_options(db=db)


@router.get("/api/articles/{article_id}", response_model=ArticleDetail)
def get_article(
    article_id: int,
    db: Connection = Depends(get_db),
    current_user_id: str = Depends(get_current_user_id),
):
    article = article_service.get_article(db=db, article_id=article_id, current_user_id=current_user_id)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    return article
