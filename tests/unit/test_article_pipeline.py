import pandas as pd
from articles.article_pipeline import ArticlePipeline


class _Reader:
    def __init__(self, rows): self.rows = rows
    def read(self): return self.rows


class _Enricher:
    def __init__(self, result): self.result = result
    def enrich(self, data): return self.result


class _Writer:
    def __init__(self): self.received = None
    def write(self, data): self.received = data


def test_pipeline_calls_read_enrich_write_in_order():
    # Arrange
    raw = [{"title": "T1"}]
    enriched = pd.DataFrame([{"title": "T1", "summary": "S"}])
    writer = _Writer()

    # Act
    ArticlePipeline(
        reader=_Reader(raw),
        enricher=_Enricher(enriched),
        writer=writer,
    ).run()

    # Assert
    assert writer.received is enriched


def test_pipeline_passes_reader_output_to_enricher():
    # Arrange
    captured = {}

    class _CapturingEnricher:
        def enrich(self, data):
            captured["data"] = data
            return pd.DataFrame()

    raw = [{"id": 1}, {"id": 2}]

    # Act
    ArticlePipeline(
        reader=_Reader(raw),
        enricher=_CapturingEnricher(),
        writer=_Writer(),
    ).run()

    # Assert
    assert captured["data"] == raw


def test_pipeline_passes_enricher_output_to_writer():
    # Arrange
    enriched = pd.DataFrame([{"x": 1}])
    writer = _Writer()

    # Act
    ArticlePipeline(
        reader=_Reader([]),
        enricher=_Enricher(enriched),
        writer=writer,
    ).run()

    # Assert
    assert writer.received is enriched
