import sqlalchemy as sa


class LikeService:
    def like_article(self, db, article_id: int, user_id: str):
        exists = db.execute(
            sa.text("SELECT TOP 1 1 FROM articles WHERE id = :id"),
            {"id": article_id},
        ).fetchone()
        if not exists:
            return None

        already_liked = db.execute(
            sa.text("""
                SELECT TOP 1 1 FROM article_likes
                WHERE article_id = :article_id AND user_id = :user_id
            """),
            {"article_id": article_id, "user_id": user_id},
        ).fetchone()

        if not already_liked:
            db.execute(
                sa.text("""
                    INSERT INTO article_likes (article_id, user_id)
                    VALUES (:article_id, :user_id)
                """),
                {"article_id": article_id, "user_id": user_id},
            )

        return self.get_like_status(db=db, article_id=article_id, user_id=user_id)

    def unlike_article(self, db, article_id: int, user_id: str):
        exists = db.execute(
            sa.text("SELECT TOP 1 1 FROM articles WHERE id = :id"),
            {"id": article_id},
        ).fetchone()
        if not exists:
            return None

        db.execute(
            sa.text("""
                DELETE FROM article_likes
                WHERE article_id = :article_id AND user_id = :user_id
            """),
            {"article_id": article_id, "user_id": user_id},
        )

        return self.get_like_status(db=db, article_id=article_id, user_id=user_id)

    def get_like_status(self, db, article_id: int, user_id: str):
        exists = db.execute(
            sa.text("SELECT TOP 1 1 FROM articles WHERE id = :id"),
            {"id": article_id},
        ).fetchone()
        if not exists:
            return None

        like_count = db.execute(
            sa.text("SELECT COUNT(id) FROM article_likes WHERE article_id = :article_id"),
            {"article_id": article_id},
        ).scalar() or 0

        liked_by_user = db.execute(
            sa.text("""
                SELECT TOP 1 1 FROM article_likes
                WHERE article_id = :article_id AND user_id = :user_id
            """),
            {"article_id": article_id, "user_id": user_id},
        ).fetchone() is not None

        return {
            "article_id":    article_id,
            "liked":         liked_by_user,
            "like_count":    int(like_count),
            "liked_by_user": liked_by_user,
        }
