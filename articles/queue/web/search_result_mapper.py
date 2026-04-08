import pandas as pd


class SearchResultMapper:
    """Maps Perplexity search results to the article_queue column shape."""

    def __init__(
        self,
        source_type: str = "web",
        source_name: str | None = None,
        sector: str | None = None,
        market_region: str | None = None,
        commodity_group: str | None = None,
        commodity_classification: str | None = None,
        max_rows: int | None = None,
    ) -> None:
        self.source_type = source_type
        self.source_name = source_name
        self.sector = sector
        self.market_region = market_region
        self.commodity_group = commodity_group
        self.commodity_classification = commodity_classification
        self.commodity_name = None  # assigned by LLM during enrichment
        self.max_rows = max_rows

    def enrich(self, results: list[dict]) -> pd.DataFrame:
        if self.max_rows is not None:
            results = results[:self.max_rows]
        rows = [
            {
                "source_type":              self.source_type,
                "source_name":              self.source_name or item.get("source_name"),
                "source_record_id":         item.get("record_id") or item.get("url"),
                "source_url":               item.get("url"),
                "title":                    item.get("title"),
                "body_text":                item.get("content"),
                "published_at":             item.get("published_at"),
                "sector":                   self.sector or item.get("sector"),
                "market_region":            self.market_region or item.get("market_region"),
                "commodity_group":          self.commodity_group or item.get("commodity_group"),
                "commodity_classification": self.commodity_classification or item.get("commodity_classification"),
                "commodity_name":           None,
            }
            for item in results
        ]
        return pd.DataFrame(rows)
