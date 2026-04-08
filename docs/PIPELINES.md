# Streamsight Pipelines

All pipelines follow the same three-step pattern configured directly in the runner:

```python
Scraper(
    request_handler=...,   # fetch / query data
    response_handler=...,  # map to standard DataFrame shape
    persistence_handler=..., # save or pass forward
).scrape()
```

---

## Web Pipeline

Searches the web for articles and saves new ones to `article_queue`.

```python
Scraper(
    request_handler=WebSearchRequestHandler(
        api_key=settings.PERPLEXITY_API_KEY,
        topics=[
            {"query": "European gas supply news", "commodity": "gas", "market_region": "Europe"},
        ],
        source_name="my_web_search",
        max_age_days=settings.MAX_AGE_DAYS,
        max_results_per_topic=settings.MAX_RESULTS_PER_TOPIC,
    ),
    response_handler=WebToCandidateResponseHandler(),
    persistence_handler=ArticleQueuePersistenceHandler(),
).scrape()
```

**Optional: restrict to trusted domains**
```python
WebSearchRequestHandler(
    ...
    domains=["naturalgasintel.com", "icis.com"],
    domain_tracker=DomainTracker(block_after_zeros=3),  # auto-blocks underperforming domains
)
```

**Optional: track LLM usage**
```python
WebSearchRequestHandler(
    ...
    usage_tracker=LlmUsageTracker(caller="my_runner"),
)
```

**Runners:** `run_web_listener.py`, `run_gas_web_listener.py`

---

## DB / API Pipeline

Takes rows from any source (DB query, API call, inline data) and saves new ones to `article_queue`.

```python
Scraper(
    request_handler=AemoRequestHandler(url=settings.AEMO_URL),
    response_handler=AemoResponseHandler(),
    persistence_handler=ArticleQueuePersistenceHandler(),
).scrape()
```

For arbitrary row sources, define an inline request handler in the runner:

```python
class MyRequestHandler(RequestHandler):
    def handle(self, **kwargs) -> list[dict]:
        return fetch_rows_from_somewhere()

Scraper(
    request_handler=MyRequestHandler(),
    response_handler=DatabaseToCandidateResponseHandler(),
    persistence_handler=ArticleQueuePersistenceHandler(),
).scrape()
```

**Runners:** `run_aemo_db_listener.py`, `run_db_listener.py`

---

## Enrichment Pipeline

Reads all pending rows from `article_queue`, summarises them via an LLM, and saves enriched articles to `articles`.

```python
Scraper(
    request_handler=ArticleQueueRequestHandler(),
    response_handler=ArticleSummaryResponseHandler(summariser=summariser),
    persistence_handler=ArticlePersistenceHandler(),
).scrape()
```

Swap the summariser in `run_article_enrichment.py`:
```python
# Dev — no API key needed
from example_dependencies import DummySummariser
summariser = DummySummariser()

# Production
from integrations.claude_summariser import ClaudeSummariser
summariser = ClaudeSummariser(api_key=settings.ANTHROPIC_API_KEY)
```

**Runner:** `run_article_enrichment.py`

---

## Persistence options

| Handler | Saves to | Dedup by |
|---|---|---|
| `ArticleQueuePersistenceHandler` | `article_queue` | `(source_type, source_name, source_record_id)` |
| `ArticlePersistenceHandler` | `articles` | `(source_type, source_name, source_record_id)` |
| `InMemoryPersistenceHandler` | nowhere | `set[str]` in memory |

Use `InMemoryPersistenceHandler` when you want to query an API and pass new records forward without saving:

```python
persistence = InMemoryPersistenceHandler(seen_keys=seen)
Scraper(request_handler, response_handler, persistence).scrape()

new_rows = persistence.new_rows
seen     = persistence.seen_keys  # carry forward to next poll
```

---

## Adding a new source

1. Create `scraper/request/my_source_request_handler.py` — implement `handle()` returning `list[dict]`
2. Reuse `DatabaseToCandidateResponseHandler` or create `scraper/response/my_source_response_handler.py`
3. Wire it up in a new runner under `runners/`
