import logging
from datetime import datetime, timedelta, timezone
from urllib.parse import urlparse

import httpx
import sqlalchemy as sa

from utils.tracking.cost_threshold import BudgetExceededError
from utils.tracking.llm_usage_tracker import LlmUsageTracker


_PERPLEXITY_URL = "https://api.perplexity.ai/chat/completions"

_SEARCH_PROMPT = """\
Find up to {max_results} recent news articles published in the last {days} days about: {query}.

For each source you cite, write a dedicated paragraph summarising that specific article's \
key facts, figures, and market angle. Start each paragraph with the citation number in brackets, \
e.g. [1] Article summary here. [2] Next article here.

Be specific — include prices, percentages, company names, and dates where available."""


from articles.queue.web.web_search_reader import WebSearchReader


class PerplexitySearch(WebSearchReader):
    def __init__(
        self,
        api_key: str,
        topics: list[dict],
        source_name: str = "web_search",
        model: str = "sonar",
        max_age_days: int = 2,
        max_results_per_topic: int = 5,
        domains: list[str] | None = None,
        usage_tracker: LlmUsageTracker | None = None,
        domain_tracker=None,
        engine=None,
        max_daily_usd: float | None = None,
        cost_tracking_enabled: bool | None = None,
    ) -> None:
        self.api_key = api_key
        self.topics = topics
        self.source_name = source_name
        self.model = model
        self.max_age_days = max_age_days
        self.max_results_per_topic = max_results_per_topic
        self.domains = domains
        self.usage_tracker = usage_tracker or LlmUsageTracker(caller=source_name)
        self.domain_tracker = domain_tracker

        if engine is None:
            from appsettings import engine as _default_engine
            engine = _default_engine
        self.engine = engine

        if max_daily_usd is None or cost_tracking_enabled is None:
            import appsettings as _settings
            max_daily_usd = max_daily_usd if max_daily_usd is not None else _settings.MAX_DAILY_LLM_SPEND_USD
            cost_tracking_enabled = cost_tracking_enabled if cost_tracking_enabled is not None else _settings.COST_TRACKING_ENABLED
        self.max_daily_usd = max_daily_usd
        self.cost_tracking_enabled = cost_tracking_enabled

    def read(self) -> list[dict]:
        self._check_budget()

        active_domains = (
            self.domain_tracker.get_active_domains(self.domains)
            if self.domain_tracker and self.domains
            else self.domains
        )

        articles = []
        skipped = 0
        for topic in self.topics:
            logging.info("[%s] searching: %s", self.source_name, topic.get("query", "custom prompt"))
            results, usage = self._search(topic, active_domains)

            self.usage_tracker.record(
                provider="perplexity",
                model=self.model,
                input_tokens=usage.get("prompt_tokens", 0),
                output_tokens=usage.get("completion_tokens", 0),
            )

            if self.domain_tracker and active_domains:
                counts = {d: 0 for d in active_domains}
                for article in results:
                    host = urlparse(article.get("url", "")).netloc.lstrip("www.")
                    for d in active_domains:
                        if d in host:
                            counts[d] += 1
                for domain, count in counts.items():
                    self.domain_tracker.record_results(domain, count)

            for article in results:
                published_at = article.get("published_at") or article.get("date")
                url = article.get("url")
                record_id = url or f"{self.source_name}_{topic.get('commodity_classification', 'global')}_{published_at}"
                if self._already_seen(record_id):
                    skipped += 1
                    continue
                articles.append({
                    "source_name":              self.source_name,
                    "url":                      url,
                    "record_id":                record_id,
                    "title":                    article.get("title"),
                    "content":                  article.get("content"),
                    "published_at":             published_at,
                    "sector":                   topic.get("sector"),
                    "commodity_group":          topic.get("commodity_group"),
                    "commodity_classification": topic.get("commodity_classification"),
                    "market_region":            topic.get("market_region"),
                })

        logging.info("[%s] %d new articles found, %d skipped (already summarised)", self.source_name, len(articles), skipped)
        return articles

    def _check_budget(self) -> None:
        if not self.cost_tracking_enabled:
            return
        spend = self.usage_tracker.get_spend(hours=24)
        limit = self.max_daily_usd
        if spend >= limit:
            raise BudgetExceededError(
                f"LLM budget exceeded: ${spend:.4f} >= ${limit:.2f} over last 24h."
            )
        logging.info("[%s] LLM spend $%.4f / $%.2f. OK.", self.source_name, spend, limit)

    def _search(self, topic: dict, domains: list[str] | None) -> tuple[list[dict], dict]:
        query = topic.get("query", "")
        prompt = topic.get("prompt") or f"Find the latest news articles about: {query}. Summarise what is happening in the market today."
        body = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.0,
            "search_recency_filter": "week",
        }
        if domains:
            body["search_domain_filter"] = domains

        response = httpx.post(
            _PERPLEXITY_URL,
            json=body,
            headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
            timeout=30.0,
        )
        response.raise_for_status()
        data = response.json()

        import re
        content = data["choices"][0]["message"]["content"].strip()
        citations = data.get("citations", [])
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        query = topic.get("query", "market update")

        # Split prose into per-citation sections on markers like [1], [2] etc.
        parts = re.split(r'\[(\d+)\]', content)
        # parts = ['intro', '1', 'text for 1', '2', 'text for 2', ...]
        citation_content: dict[int, str] = {}
        i = 1
        while i < len(parts) - 1:
            try:
                idx = int(parts[i])
                citation_content[idx] = parts[i + 1].strip()
                i += 2
            except (ValueError, IndexError):
                i += 1

        results = []
        for idx, url in enumerate(citations[:self.max_results_per_topic], start=1):
            article_content = citation_content.get(idx) or content
            results.append({
                "title":        f"{query} — {today}",
                "url":          url,
                "content":      article_content,
                "published_at": today,
            })

        if not results:
            results = [{
                "title":        f"Market Update — {today}",
                "url":          None,
                "content":      content,
                "published_at": today,
            }]

        return results, data.get("usage", {})

    def _already_seen(self, record_id: str) -> bool:
        with self.engine.connect() as conn:
            return conn.execute(
                sa.text("SELECT TOP 1 1 FROM articles WHERE record_id = :id"),
                {"id": record_id},
            ).fetchone() is not None

    def _too_old(self, published_at: str | None) -> bool:
        if not published_at:
            return False
        try:
            dt = datetime.fromisoformat(published_at.replace("Z", "+00:00"))
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt < datetime.now(timezone.utc) - timedelta(days=self.max_age_days)
        except (ValueError, TypeError):
            return False
