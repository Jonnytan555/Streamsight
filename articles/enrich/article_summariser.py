import pandas as pd

from utils.tracking.llm_usage_tracker import LlmUsageTracker
from utils.tracking.budget_checker import BudgetChecker


class ArticleSummariser:
    def __init__(
        self,
        summariser,
        budget_checker: BudgetChecker | None = None,
        usage_tracker: LlmUsageTracker | None = None,
    ) -> None:
        self.summariser     = summariser
        self.usage_tracker  = usage_tracker or LlmUsageTracker(caller="article_enrichment")
        self.budget_checker = budget_checker

    def enrich(self, articles: list[dict]) -> pd.DataFrame:
        if self.budget_checker:
            self.budget_checker.check()

        rows = []
        for item in articles:
            summary = self.summariser.summarise(
                title=item.get("title"),
                body_text=item.get("body_text"),
                sector=item.get("sector"),
                market_region=item.get("market_region"),
                commodity_group=item.get("commodity_group"),
                commodity_classification=item.get("commodity_classification"),
            )

            if hasattr(self.summariser, "last_usage"):
                usage = self.summariser.last_usage
                self.usage_tracker.record(
                    provider=usage.get("provider", "anthropic"),
                    model=usage.get("model", "unknown"),
                    input_tokens=usage.get("input_tokens", 0),
                    output_tokens=usage.get("output_tokens", 0),
                )

            rows.append({
                "article_id":               item.get("article_candidate_id"),
                "record_id":                item.get("source_record_id"),
                "source_type":              item.get("source_type"),
                "source_name":              item.get("source_name"),
                "url":                      item.get("source_url"),
                "title":                    item.get("title"),
                "published_at":             item.get("published_at"),
                "summary":                  summary["short_summary"],
                "sector":                   item.get("sector"),
                "commodity_group":          self._first(summary.get("commodity_group")) or item.get("commodity_group"),
                "commodity_classification": self._first(summary.get("commodity_classification")) or item.get("commodity_classification"),
                "commodity_name":           self._first(summary.get("commodity_name")) or item.get("commodity_name"),
            })
        return pd.DataFrame(rows)

    @staticmethod
    def _first(value):
        """Return first element if value is a list, otherwise value as-is."""
        if isinstance(value, list):
            return value[0] if value else None
        return value
