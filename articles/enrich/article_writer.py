import logging
import math
import sqlalchemy as sa
import pandas as pd

from appsettings import engine as _default_engine, ARTICLE_KEY_COLS


from scraper.persistence.db_upsert_handler import DbUpsertHandler as _Base


_DB_COLS = [
    "article_id", "record_id", "source_type", "source_name",
    "url", "title", "summary", "published_at",
    "sector", "commodity_group", "commodity_classification", "commodity_name",
]


class ArticleWriter(_Base):
    def __init__(self, engine=None) -> None:
        super().__init__(
            engine=engine or _default_engine,
            table_name="articles",
            schema="dbo",
            key_cols=ARTICLE_KEY_COLS,
        )

    def write(self, enriched: pd.DataFrame) -> list[dict]:
        if enriched is None or enriched.empty:
            return []

        db_df = enriched[_DB_COLS].copy()
        db_df = db_df.dropna(subset=ARTICLE_KEY_COLS, how="any")

        inserted = self._insert_new(db_df)

        # Mark all queue items processed — including duplicates that already exist
        # in the articles table. Without this they stay 'pending' and get re-enriched
        # on every run.
        all_candidate_ids = db_df["article_id"].dropna().astype(int).tolist()
        self._mark_queue_processed(all_candidate_ids)

        if inserted:
            self._insert_tags(inserted, enriched)

        return [{"id": r["id"], "title": r["title"]} for r in inserted]

    def _insert_tags(self, inserted: list[dict], enriched: pd.DataFrame) -> None:
        enriched_idx = enriched.set_index("record_id")

        with self.engine.begin() as conn:
            for row in inserted:
                article_id = row["id"]
                record_id  = row.get("record_id")

                try:
                    article_row = enriched_idx.loc[record_id]
                except KeyError:
                    continue

                tree_id = self._lookup_tree_id(
                    conn,
                    article_row.get("sector"),
                    article_row.get("commodity_group"),
                    article_row.get("commodity_classification"),
                    article_row.get("commodity_name"),
                )

                if tree_id:
                    conn.execute(
                        sa.text("""
                            IF NOT EXISTS (
                                SELECT 1 FROM dbo.article_tags
                                WHERE article_id = :article_id AND commodity_tree_id = :tree_id
                            )
                            INSERT INTO dbo.article_tags (article_id, commodity_tree_id)
                            VALUES (:article_id, :tree_id)
                        """),
                        {"article_id": article_id, "tree_id": tree_id},
                    )

    def _lookup_tree_id(
        self,
        conn,
        sector: str | None,
        commodity_group: str | None,
        commodity_classification: str | None,
        commodity_name: str | None,
    ) -> int | None:
        # LLM may return lists or pandas NaN for any taxonomy field — normalise all to str | None
        def _clean(v):
            if isinstance(v, list):
                v = v[0] if v else None
            if v is None:
                return None
            if isinstance(v, float) and math.isnan(v):
                return None
            return v

        sector                   = _clean(sector)
        commodity_group          = _clean(commodity_group)
        commodity_classification = _clean(commodity_classification)
        commodity_name           = _clean(commodity_name)

        conditions = []
        params = {}

        if sector:
            conditions.append("sector = :sector")
            params["sector"] = sector
        if commodity_group:
            conditions.append("commodity_group = :commodity_group")
            params["commodity_group"] = commodity_group
        if commodity_classification:
            conditions.append("commodity_classification = :commodity_classification")
            params["commodity_classification"] = commodity_classification
        if commodity_name:
            conditions.append("commodity_name = :commodity_name")
            params["commodity_name"] = commodity_name

        if not conditions:
            return None

        where = " AND ".join(conditions) + " AND is_active = 1"
        result = conn.execute(
            sa.text(f"SELECT TOP 1 id FROM dbo.commodity_tree WHERE {where} ORDER BY level DESC"),
            params,
        ).fetchone()

        if not result:
            logging.debug("[ArticleWriter] No commodity_tree match for %s/%s/%s/%s",
                          sector, commodity_group, commodity_classification, commodity_name)
        return result[0] if result else None

    def _mark_queue_processed(self, candidate_ids: list) -> None:
        if not candidate_ids:
            return
        with self.engine.begin() as conn:
            conn.execute(
                sa.text("UPDATE article_queue SET status = 'processed' WHERE id = :id"),
                [{"id": cid} for cid in candidate_ids],
            )
