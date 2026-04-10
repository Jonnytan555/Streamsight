import pandas as pd

from appsettings import engine as _default_engine, QUEUE_KEY_COLS


from scraper.persistence.db_persistence_handler import DbPersistenceHandler as _Base


_DB_COLS = [
    "source_type", "source_name", "source_record_id", "source_url",
    "title", "body_text", "published_at", "sector", "market_region",
    "commodity_group", "commodity_classification", "commodity_name", "status",
]


class QueueWriter(_Base):
    def __init__(self, engine=None) -> None:
        super().__init__(
            engine=engine or _default_engine,
            table_name="article_queue",
            schema="dbo",
            key_cols=QUEUE_KEY_COLS,
        )

    def write(self, mapped: pd.DataFrame) -> list[dict]:
        if mapped is None or mapped.empty:
            return []

        db_df = mapped.copy()
        db_df["status"] = "pending"
        db_df = db_df[_DB_COLS]
        db_df = db_df.dropna(subset=QUEUE_KEY_COLS, how="any")

        inserted = self._insert_new(db_df)

        return [
            {
                "article_candidate_id":     r["id"],
                "source_type":              r["source_type"],
                "source_name":              r["source_name"],
                "source_record_id":         r["source_record_id"],
                "source_url":               r["source_url"],
                "title":                    r["title"],
                "body_text":                r["body_text"],
                "published_at":             r["published_at"],
                "sector":                   r["sector"],
                "commodity_group":          r["commodity_group"],
                "commodity_classification": r["commodity_classification"],
                "commodity_name":           r["commodity_name"],
                "market_region":            r["market_region"],
                "status":                   r["status"],
            }
            for r in inserted
        ]
