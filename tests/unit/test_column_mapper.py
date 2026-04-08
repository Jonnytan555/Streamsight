import pytest
from articles.queue.db.column_mapper import ColumnMapper


_VALID_MAP = {
    "source_type":              "database",
    "source_name":              "aemo",
    "source_record_id":         lambda r: r["id"],
    "source_url":               "http://example.com",
    "title":                    lambda r: f"Title {r['id']}",
    "body_text":                lambda r: f"Body {r['id']}",
    "published_at":             "2026-01-01",
    "sector":                   "Energy",
    "market_region":            "Australia",
    "commodity_group":          "Natural Gas",
    "commodity_classification": "Australian Gas",
}


def test_enrich_maps_literals():
    mapper = ColumnMapper(_VALID_MAP)
    result = mapper.enrich([{"id": 1}])
    assert result.iloc[0]["source_type"] == "database"
    assert result.iloc[0]["sector"] == "Energy"


def test_enrich_maps_callables():
    mapper = ColumnMapper(_VALID_MAP)
    result = mapper.enrich([{"id": 42}])
    assert result.iloc[0]["source_record_id"] == 42
    assert result.iloc[0]["title"] == "Title 42"


def test_enrich_multiple_rows():
    mapper = ColumnMapper(_VALID_MAP)
    result = mapper.enrich([{"id": 1}, {"id": 2}])
    assert len(result) == 2
    assert result.iloc[1]["title"] == "Title 2"


def test_enrich_optional_commodity_name():
    column_map = {**_VALID_MAP, "commodity_name": "AEMO"}
    mapper = ColumnMapper(column_map)
    result = mapper.enrich([{"id": 1}])
    assert result.iloc[0]["commodity_name"] == "AEMO"


def test_missing_required_key_raises():
    incomplete = {k: v for k, v in _VALID_MAP.items() if k != "sector"}
    with pytest.raises(ValueError, match="sector"):
        ColumnMapper(incomplete)


def test_empty_rows_returns_empty_dataframe():
    mapper = ColumnMapper(_VALID_MAP)
    result = mapper.enrich([])
    assert result.empty
