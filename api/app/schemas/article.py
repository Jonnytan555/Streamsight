from pydantic import BaseModel


class ArticleFeedItem(BaseModel):
    id: int
    title: str | None = None
    summary: str | None = None
    commodity_group: str | None = None
    commodity_classification: str | None = None
    commodity_name: str | None = None
    published_at: str | None = None
    url: str | None = None
    like_count: int = 0
    liked_by_user: bool = False


class ArticleDetail(BaseModel):
    id: int
    title: str | None = None
    summary: str | None = None
    source_type: str | None = None
    source_name: str | None = None
    sector: str | None = None
    commodity_group: str | None = None
    commodity_classification: str | None = None
    commodity_name: str | None = None
    published_at: str | None = None
    url: str | None = None
    like_count: int = 0
    liked_by_user: bool = False
