import sqlalchemy as sa


class QueueReader:
    """Reads pending rows from article_queue, optionally filtered by source_type."""

    def __init__(self, source_type: str | None = None, engine=None) -> None:
        self.source_type = source_type
        if engine is None:
            from appsettings import engine as _default_engine
            engine = _default_engine
        self.engine = engine

    def read(self) -> list[dict]:
        query = """
            SELECT id, source_type, source_name, source_record_id,
                   source_url, title, body_text, published_at,
                   sector, market_region, commodity_group, commodity_classification, commodity_name
            FROM article_queue
            WHERE status = 'pending'
        """
        params = {}
        if self.source_type:
            query += " AND source_type = :source_type"
            params["source_type"] = self.source_type

        with self.engine.connect() as conn:
            rows = conn.execute(sa.text(query), params).fetchall()

        return [
            {
                "article_candidate_id":     r.id,
                "source_type":              r.source_type,
                "source_name":              r.source_name,
                "source_record_id":         r.source_record_id,
                "source_url":               r.source_url,
                "title":                    r.title,
                "body_text":                r.body_text,
                "published_at":             r.published_at,
                "sector":                   r.sector,
                "market_region":            r.market_region,
                "commodity_group":          r.commodity_group,
                "commodity_classification": r.commodity_classification,
                "commodity_name":           r.commodity_name,
            }
            for r in rows
        ]
