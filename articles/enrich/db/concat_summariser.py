class ConcatSummariser:
    """Passes through existing text as the summary without calling any LLM."""

    def summarise(
        self,
        title: str,
        body_text: str,
        commodity_group: str | None = None,
        commodity_classification: str | None = None,
        **_,
    ) -> dict:
        summary = (body_text or title or "").strip()[:500]
        return {
            "short_summary":            summary,
            "commodity_group":          commodity_group,
            "commodity_classification": commodity_classification,
            "commodity_name":           None,
        }
