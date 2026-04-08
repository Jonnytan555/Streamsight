from pydantic import BaseModel


class LikeResponse(BaseModel):
    article_id: int
    liked: bool
    like_count: int
    liked_by_user: bool
