import pandas as pd
import pytest
from articles.enrich.article_summariser import ArticleSummariser
from utils.tracking.budget_checker import BudgetChecker


class _FakeSummariser:
    last_usage = {}

    def summarise(self, title, body_text, **kwargs):
        return {
            "short_summary":            f"Summary of {title}",
            "commodity_group":          "Natural Gas",
            "commodity_classification": "European Gas",
            "commodity_name":           "TTF",
        }


class _BudgetOk(BudgetChecker):
    def check(self): pass


class _BudgetExceeded(BudgetChecker):
    def check(self): raise RuntimeError("Budget exceeded")


def _item(**kwargs):
    defaults = dict(
        article_candidate_id=1,
        source_type="web",
        source_name="gas_web",
        source_record_id="https://example.com/1",
        source_url="https://example.com/1",
        title="TTF falls",
        body_text="TTF prices dropped 2%",
        published_at="2026-04-04",
        sector="Energy",
        market_region="Global",
        commodity_group="Natural Gas",
        commodity_classification="European Gas",
        commodity_name=None,
    )
    return {**defaults, **kwargs}


def test_enrich_returns_dataframe():
    # Arrange
    summariser = ArticleSummariser(summariser=_FakeSummariser())

    # Act
    result = summariser.enrich([_item()])

    # Assert
    assert isinstance(result, pd.DataFrame)
    assert len(result) == 1


def test_enrich_sets_summary_from_summariser():
    # Arrange
    summariser = ArticleSummariser(summariser=_FakeSummariser())

    # Act
    result = summariser.enrich([_item(title="TTF falls")])

    # Assert
    assert result.iloc[0]["summary"] == "Summary of TTF falls"


def test_enrich_sets_taxonomy_from_summariser():
    # Arrange
    summariser = ArticleSummariser(summariser=_FakeSummariser())

    # Act
    result = summariser.enrich([_item()])

    # Assert
    assert result.iloc[0]["commodity_name"] == "TTF"


def test_enrich_falls_back_to_queue_taxonomy_when_summariser_returns_none():
    # Arrange
    class _NullSummariser:
        last_usage = {}
        def summarise(self, **kwargs):
            return {"short_summary": "S", "commodity_group": None,
                    "commodity_classification": None, "commodity_name": None}

    summariser = ArticleSummariser(summariser=_NullSummariser())

    # Act
    result = summariser.enrich([_item(commodity_name="AEMO")])

    # Assert
    assert result.iloc[0]["commodity_name"] == "AEMO"


def test_budget_check_called_before_summarising():
    # Arrange
    summariser = ArticleSummariser(
        summariser=_FakeSummariser(),
        budget_checker=_BudgetExceeded(),
    )

    # Act / Assert
    with pytest.raises(RuntimeError, match="Budget exceeded"):
        summariser.enrich([_item()])


def test_no_budget_checker_skips_check():
    # Arrange
    summariser = ArticleSummariser(summariser=_FakeSummariser())

    # Act
    result = summariser.enrich([_item()])

    # Assert
    assert not result.empty


def test_sector_passed_through_from_queue():
    # Arrange
    summariser = ArticleSummariser(summariser=_FakeSummariser())

    # Act
    result = summariser.enrich([_item(sector="Agriculture")])

    # Assert
    assert result.iloc[0]["sector"] == "Agriculture"


def test_empty_articles_returns_empty_dataframe():
    # Arrange
    summariser = ArticleSummariser(summariser=_FakeSummariser())

    # Act
    result = summariser.enrich([])

    # Assert
    assert result.empty
