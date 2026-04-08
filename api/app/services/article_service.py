import sqlalchemy as sa


class ArticleService:
    def get_articles(
        self,
        db,
        current_user_id: str | None = None,
        commodity_group: str | None = None,
        commodity_classification: str | None = None,
        skip: int = 0,
        limit: int = 20,
    ):
        rows = db.execute(
            sa.text("""
                SELECT
                    a.id, a.title, a.summary,
                    a.commodity_group, a.commodity_classification, a.commodity_name,
                    a.published_at, a.url,
                    COUNT(al.id) AS like_count,
                    MAX(CASE WHEN al.user_id = :user_id THEN 1 ELSE 0 END) AS liked_by_user
                FROM articles a
                LEFT JOIN article_likes al ON al.article_id = a.id
                WHERE (:commodity_group IS NULL OR a.commodity_group = :commodity_group)
                  AND (:commodity_classification IS NULL OR a.commodity_classification = :commodity_classification)
                GROUP BY
                    a.id, a.title, a.summary,
                    a.commodity_group, a.commodity_classification, a.commodity_name,
                    a.published_at, a.url, a.created_at
                ORDER BY a.created_at DESC
                OFFSET :skip ROWS FETCH NEXT :limit ROWS ONLY
            """),
            {
                "user_id":                  current_user_id,
                "commodity_group":          commodity_group,
                "commodity_classification": commodity_classification,
                "skip":                     skip,
                "limit":                    limit,
            },
        ).fetchall()

        return [
            {
                "id":                       r.id,
                "title":                    r.title,
                "summary":                  r.summary,
                "commodity_group":          r.commodity_group,
                "commodity_classification": r.commodity_classification,
                "commodity_name":           r.commodity_name,
                "published_at":             r.published_at,
                "url":                      r.url,
                "like_count":               int(r.like_count or 0),
                "liked_by_user":            bool(r.liked_by_user or 0),
            }
            for r in rows
        ]

    def get_article(self, db, article_id: int, current_user_id: str | None = None):
        row = db.execute(
            sa.text("""
                SELECT
                    a.id, a.title, a.summary,
                    a.source_type, a.source_name,
                    a.sector, a.commodity_group, a.commodity_classification, a.commodity_name,
                    a.published_at, a.url,
                    COUNT(al.id) AS like_count,
                    MAX(CASE WHEN al.user_id = :user_id THEN 1 ELSE 0 END) AS liked_by_user
                FROM articles a
                LEFT JOIN article_likes al ON al.article_id = a.id
                WHERE a.id = :article_id
                GROUP BY
                    a.id, a.title, a.summary,
                    a.source_type, a.source_name,
                    a.sector, a.commodity_group, a.commodity_classification, a.commodity_name,
                    a.published_at, a.url
            """),
            {"user_id": current_user_id, "article_id": article_id},
        ).fetchone()

        if not row:
            return None

        return {
            "id":                       row.id,
            "title":                    row.title,
            "summary":                  row.summary,
            "source_type":              row.source_type,
            "source_name":              row.source_name,
            "sector":                   row.sector,
            "commodity_group":          row.commodity_group,
            "commodity_classification": row.commodity_classification,
            "commodity_name":           row.commodity_name,
            "published_at":             row.published_at,
            "url":                      row.url,
            "like_count":               int(row.like_count or 0),
            "liked_by_user":            bool(row.liked_by_user or 0),
        }

    def get_filter_options(self, db):
        groups = [
            r[0] for r in db.execute(
                sa.text("SELECT DISTINCT commodity_group FROM articles WHERE commodity_group IS NOT NULL")
            ).fetchall()
        ]
        classifications = [
            r[0] for r in db.execute(
                sa.text("SELECT DISTINCT commodity_classification FROM articles WHERE commodity_classification IS NOT NULL")
            ).fetchall()
        ]
        return {
            "commodity_groups":          sorted(groups),
            "commodity_classifications": sorted(classifications),
        }
