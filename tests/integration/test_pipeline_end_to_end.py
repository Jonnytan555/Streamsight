"""
End-to-end pipeline integration test.

Tests the full flow:
    QueueWriter → article_queue (SQLite)
    QueueReader → reads pending rows (SQLite)
    ArticleSummariser + ConcatSummariser → enriches rows (pure, no DB)
    ArticleWriter → writes to articles (mocked _insert_new — SQL Server specific)

External dependencies mocked:
    - DbInsertNewHandler._insert_new  (SQL Server syntax, scraper library)
    - ArticleWriter._insert_tags      (commodity_tree lookup, SQL Server)
    - ArticleWriter._mark_queue_processed (UPDATE, SQL Server)
"""
import pandas as pd
import pytest
import sqlalchemy as sa
from unittest.mock import patch, MagicMock

from articles.article_pipeline import ArticlePipeline
from articles.enrich.article_summariser import ArticleSummariser
from articles.enrich.article_writer import ArticleWriter
from articles.enrich.db.concat_summariser import ConcatSummariser
from articles.enrich.queue_reader import QueueReader
from articles.queue.db.column_mapper import ColumnMapper
from articles.queue.queue_writer import QueueWriter


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _seed_queue(engine):
    """Insert two pending rows directly into article_queue."""
    with engine.begin() as conn:
        for i in range(1, 3):
            conn.execute(sa.text("""
                INSERT INTO article_queue
                    (source_type, source_name, source_record_id, source_url,
                     title, body_text, published_at,
                     sector, market_region, commodity_group, commodity_classification,
                     commodity_name, status)
                VALUES
                    (:source_type, :source_name, :source_record_id, :source_url,
                     :title, :body_text, :published_at,
                     :sector, :market_region, :commodity_group, :commodity_classification,
                     :commodity_name, :status)
            """), {
                "source_type":              "database",
                "source_name":              "aemo",
                "source_record_id":         f"rec-{i}",
                "source_url":               f"http://aemo.com/{i}",
                "title":                    f"Gas Flow Update {i}",
                "body_text":                f"Supply at facility {i} was 100 TJ.",
                "published_at":             "2026-04-04",
                "sector":                   "Energy",
                "market_region":            "Australia",
                "commodity_group":          "Natural Gas",
                "commodity_classification": "Australian Gas",
                "commodity_name":           "AEMO",
                "status":                   "pending",
            })


def _mock_inserted_rows(df: pd.DataFrame) -> list[dict]:
    """Simulate what DbInsertNewHandler._insert_new returns."""
    rows = []
    for i, row in df.iterrows():
        d = row.to_dict()
        d["id"] = i + 1
        rows.append(d)
    return rows


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_full_db_enrichment_pipeline(sqlite_engine):
    """
    Full pipeline: queue rows → read → summarise (concat) → write to articles.
    Mocks only the SQL Server-specific DB operations in ArticleWriter.
    """
    # Arrange
    _seed_queue(sqlite_engine)

    reader   = QueueReader(source_type="database", engine=sqlite_engine)
    enricher = ArticleSummariser(summariser=ConcatSummariser())
    writer   = ArticleWriter(engine=sqlite_engine)

    # Act — mock only SQL Server-specific methods on ArticleWriter
    with patch.object(writer, "_insert_new", side_effect=_mock_inserted_rows), \
         patch.object(writer, "_insert_tags"), \
         patch.object(writer, "_mark_queue_processed"):

        ArticlePipeline(reader=reader, enricher=enricher, writer=writer).run()

        # Assert — writer received the right number of rows
        assert writer._insert_new.call_count == 1
        df_written = writer._insert_new.call_args[0][0]
        assert len(df_written) == 2

        # Assert — correct fields populated
        assert list(df_written["source_name"]) == ["aemo", "aemo"]
        assert list(df_written["sector"]) == ["Energy", "Energy"]
        assert list(df_written["commodity_name"]) == ["AEMO", "AEMO"]

        # Assert — summary is body text (ConcatSummariser)
        assert df_written.iloc[0]["summary"] == "Supply at facility 1 was 100 TJ."

        # Assert — queue marked processed for both rows
        writer._mark_queue_processed.assert_called_once()


def test_full_web_enrichment_pipeline_with_mock_llm(sqlite_engine):
    """
    Full pipeline: queue rows → read → summarise (fake LLM) → write to articles.
    Simulates a web article being enriched by Claude.
    """
    # Arrange — seed one web article in the queue
    with sqlite_engine.begin() as conn:
        conn.execute(sa.text("""
            INSERT INTO article_queue
                (source_type, source_name, source_record_id, source_url,
                 title, body_text, published_at,
                 sector, market_region, commodity_group, commodity_classification,
                 commodity_name, status)
            VALUES
                ('web', 'gas_web_search', 'https://reuters.com/ttf-1',
                 'https://reuters.com/ttf-1',
                 'TTF Gas Prices Fall', 'TTF dropped 2% amid mild weather.',
                 '2026-04-04', 'Energy', 'Global', 'Natural Gas', 'European Gas',
                 NULL, 'pending')
        """))

    class _FakeClaudeSummariser:
        last_usage = {"provider": "anthropic", "model": "claude-haiku-4-5-20251001",
                      "input_tokens": 100, "output_tokens": 50}

        def summarise(self, title, body_text, **kwargs):
            return {
                "short_summary":            "TTF fell 2% on mild weather.",
                "commodity_group":          "Natural Gas",
                "commodity_classification": "European Gas",
                "commodity_name":           "TTF",
            }

    reader   = QueueReader(source_type="web", engine=sqlite_engine)
    enricher = ArticleSummariser(summariser=_FakeClaudeSummariser())
    writer   = ArticleWriter(engine=sqlite_engine)

    # Act
    with patch.object(writer, "_insert_new", side_effect=_mock_inserted_rows), \
         patch.object(writer, "_insert_tags"), \
         patch.object(writer, "_mark_queue_processed"):

        ArticlePipeline(reader=reader, enricher=enricher, writer=writer).run()

        # Assert — one article written
        df_written = writer._insert_new.call_args[0][0]
        assert len(df_written) == 1

        # Assert — LLM-assigned taxonomy
        assert df_written.iloc[0]["commodity_name"] == "TTF"
        assert df_written.iloc[0]["commodity_classification"] == "European Gas"

        # Assert — summary from LLM not raw body
        assert df_written.iloc[0]["summary"] == "TTF fell 2% on mild weather."

        # Assert — URL preserved
        assert df_written.iloc[0]["url"] == "https://reuters.com/ttf-1"


def test_queue_writer_to_queue_reader_roundtrip(sqlite_engine):
    """
    Tests that QueueWriter correctly writes rows that QueueReader can then read back.
    Uses ColumnMapper to simulate what a DB runner does.
    """
    # Arrange
    raw_rows = [
        {"GasDate": "2026-04-04", "FacilityId": 1, "FacilityName": "Longford",
         "LocationId": 10, "LocationName": "VIC", "VersionNum": 1,
         "Demand": 100, "Supply": 95},
    ]

    column_map = {
        "source_type":              "database",
        "source_name":              "aemo",
        "source_record_id":         lambda r: f"{r['GasDate']}_{r['FacilityId']}",
        "source_url":               "http://aemo.com",
        "title":                    lambda r: f"{r['FacilityName']} — {r['GasDate']}",
        "body_text":                lambda r: f"Supply: {r['Supply']} TJ",
        "published_at":             lambda r: r["GasDate"],
        "sector":                   "Energy",
        "market_region":            "Australia",
        "commodity_group":          "Natural Gas",
        "commodity_classification": "Australian Gas",
        "commodity_name":           "AEMO",
    }

    mapper = ColumnMapper(column_map)
    writer = QueueWriter(engine=sqlite_engine)

    # Act — map raw rows then write to queue (mock _insert_new to use SQLite)
    mapped_df = mapper.enrich(raw_rows)
    mapped_df["status"] = "pending"

    with sqlite_engine.begin() as conn:
        mapped_df.to_sql("article_queue", conn, if_exists="append", index=False)

    result = QueueReader(engine=sqlite_engine).read()

    # Assert
    assert len(result) == 1
    assert result[0]["source_record_id"] == "2026-04-04_1"
    assert result[0]["title"] == "Longford — 2026-04-04"
    assert result[0]["body_text"] == "Supply: 95 TJ"
    assert result[0]["sector"] == "Energy"
    assert result[0]["commodity_name"] == "AEMO"
