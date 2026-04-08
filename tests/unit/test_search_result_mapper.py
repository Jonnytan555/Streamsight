from articles.queue.web.search_result_mapper import SearchResultMapper


def _mapper(**kwargs):
    defaults = dict(
        source_type="web",
        source_name="gas_web_search",
        sector="Energy",
        market_region="Global",
        commodity_group="Natural Gas",
        commodity_classification="European Gas",
    )
    return SearchResultMapper(**{**defaults, **kwargs})


def _item(**kwargs):
    defaults = dict(
        url="https://reuters.com/article/1",
        title="Gas prices fall",
        content="TTF dropped 2%",
        published_at="2026-04-04",
    )
    return {**defaults, **kwargs}


def test_maps_basic_fields():
    result = _mapper().enrich([_item()])
    row = result.iloc[0]
    assert row["source_type"] == "web"
    assert row["source_name"] == "gas_web_search"
    assert row["title"] == "Gas prices fall"
    assert row["body_text"] == "TTF dropped 2%"
    assert row["source_url"] == "https://reuters.com/article/1"


def test_record_id_uses_url():
    result = _mapper().enrich([_item()])
    assert result.iloc[0]["source_record_id"] == "https://reuters.com/article/1"


def test_record_id_falls_back_to_record_id_field():
    result = _mapper().enrich([_item(url=None, record_id="custom-id")])
    assert result.iloc[0]["source_record_id"] == "custom-id"


def test_taxonomy_from_mapper_overrides_item():
    result = _mapper(commodity_group="Oil").enrich([_item(commodity_group="Gas")])
    assert result.iloc[0]["commodity_group"] == "Oil"


def test_max_rows_limits_results():
    items = [_item(url=f"https://example.com/{i}") for i in range(10)]
    result = _mapper(max_rows=3).enrich(items)
    assert len(result) == 3


def test_commodity_name_is_none():
    result = _mapper().enrich([_item()])
    assert result.iloc[0]["commodity_name"] is None


def test_empty_results():
    result = _mapper().enrich([])
    assert result.empty
