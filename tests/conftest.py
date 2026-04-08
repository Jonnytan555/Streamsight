"""
Shared fixtures for unit and integration tests.

Unit tests:   use in-memory SQLite engine via `sqlite_engine`
Integration:  use real STREAMSIGHT DB (requires connection)
"""
import pytest
import sqlalchemy as sa


@pytest.fixture
def sqlite_engine():
    """In-memory SQLite engine with the minimal schema needed for tests."""
    engine = sa.create_engine("sqlite:///:memory:")
    with engine.begin() as conn:
        conn.execute(sa.text("""
            CREATE TABLE article_queue (
                id               INTEGER PRIMARY KEY AUTOINCREMENT,
                source_type      TEXT NOT NULL,
                source_name      TEXT NOT NULL,
                source_record_id TEXT NOT NULL,
                source_url       TEXT,
                title            TEXT,
                body_text        TEXT,
                published_at     TEXT,
                sector           TEXT,
                market_region    TEXT,
                commodity_group  TEXT,
                commodity_classification TEXT,
                commodity_name   TEXT,
                status           TEXT NOT NULL DEFAULT 'pending'
            )
        """))
        conn.execute(sa.text("""
            CREATE TABLE articles (
                id                       INTEGER PRIMARY KEY AUTOINCREMENT,
                article_id               INTEGER,
                record_id                TEXT NOT NULL,
                source_type              TEXT NOT NULL,
                source_name              TEXT NOT NULL,
                url                      TEXT,
                title                    TEXT,
                summary                  TEXT,
                published_at             TEXT,
                sector                   TEXT,
                commodity_group          TEXT,
                commodity_classification TEXT,
                commodity_name           TEXT,
                created_at               TEXT DEFAULT CURRENT_TIMESTAMP,
                UNIQUE (source_type, source_name, record_id)
            )
        """))
        conn.execute(sa.text("""
            CREATE TABLE llm_usage (
                id                  INTEGER PRIMARY KEY AUTOINCREMENT,
                provider            TEXT,
                model               TEXT,
                caller              TEXT,
                input_tokens        INTEGER,
                output_tokens       INTEGER,
                estimated_cost_usd  REAL,
                called_at           TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """))
    yield engine
    engine.dispose()
