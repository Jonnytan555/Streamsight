import sqlalchemy as sa
from articles.enrich.queue_reader import QueueReader


def _insert_queue_row(conn, **kwargs):
    defaults = dict(
        source_type="database", source_name="aemo",
        source_record_id="rec-1", source_url="http://x.com",
        title="Title", body_text="Body", published_at="2026-01-01",
        sector="Energy", market_region="Australia",
        commodity_group="Natural Gas", commodity_classification="Australian Gas",
        commodity_name="AEMO", status="pending",
    )
    row = {**defaults, **kwargs}
    conn.execute(sa.text("""
        INSERT INTO article_queue
            (source_type, source_name, source_record_id, source_url,
             title, body_text, published_at, sector, market_region,
             commodity_group, commodity_classification, commodity_name, status)
        VALUES
            (:source_type, :source_name, :source_record_id, :source_url,
             :title, :body_text, :published_at, :sector, :market_region,
             :commodity_group, :commodity_classification, :commodity_name, :status)
    """), row)


def test_reads_pending_rows(sqlite_engine):
    # Arrange
    with sqlite_engine.begin() as conn:
        _insert_queue_row(conn)

    # Act
    result = QueueReader(engine=sqlite_engine).read()

    # Assert
    assert len(result) == 1
    assert result[0]["source_name"] == "aemo"


def test_filters_by_source_type(sqlite_engine):
    # Arrange
    with sqlite_engine.begin() as conn:
        _insert_queue_row(conn, source_type="database", source_record_id="rec-1")
        _insert_queue_row(conn, source_type="web", source_record_id="rec-2")

    # Act
    result = QueueReader(source_type="web", engine=sqlite_engine).read()

    # Assert
    assert len(result) == 1
    assert result[0]["source_type"] == "web"


def test_skips_processed_rows(sqlite_engine):
    # Arrange
    with sqlite_engine.begin() as conn:
        _insert_queue_row(conn, status="processed")

    # Act
    result = QueueReader(engine=sqlite_engine).read()

    # Assert
    assert len(result) == 0


def test_returns_all_fields(sqlite_engine):
    # Arrange
    with sqlite_engine.begin() as conn:
        _insert_queue_row(conn)

    # Act
    row = QueueReader(engine=sqlite_engine).read()[0]

    # Assert
    assert row["sector"] == "Energy"
    assert row["commodity_name"] == "AEMO"
    assert row["commodity_classification"] == "Australian Gas"
