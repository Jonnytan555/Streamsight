from articles.enrich.db.concat_summariser import ConcatSummariser


def test_uses_body_text_as_summary():
    result = ConcatSummariser().summarise(title="T", body_text="Some body text")
    assert result["short_summary"] == "Some body text"


def test_falls_back_to_title_when_no_body():
    result = ConcatSummariser().summarise(title="My Title", body_text=None)
    assert result["short_summary"] == "My Title"


def test_truncates_to_500_chars():
    long_text = "x" * 600
    result = ConcatSummariser().summarise(title="T", body_text=long_text)
    assert len(result["short_summary"]) == 500


def test_passes_through_taxonomy():
    result = ConcatSummariser().summarise(
        title="T",
        body_text="B",
        commodity_group="Natural Gas",
        commodity_classification="European Gas",
    )
    assert result["commodity_group"] == "Natural Gas"
    assert result["commodity_classification"] == "European Gas"
    assert result["commodity_name"] is None


def test_absorbs_extra_kwargs():
    result = ConcatSummariser().summarise(
        title="T", body_text="B", sector="Energy", market_region="Global"
    )
    assert "short_summary" in result


def test_empty_inputs_return_empty_summary():
    result = ConcatSummariser().summarise(title=None, body_text=None)
    assert result["short_summary"] == ""
