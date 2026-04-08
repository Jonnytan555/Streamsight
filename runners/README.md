# Runners

Each runner is a self-contained ingest pipeline that pulls data from one source and writes it to the article queue.

## Structure

```
runners/
  web/          Web search runners (Perplexity)
  db/           Database / API runners
```

Each runner has its own folder containing:
- `run.py` — entry point, wired into an Airflow DAG
- `appsettings.py` — runner-specific config, inherits from root `appsettings.py`
- `response_handler.py` — optional, only if the source needs custom column mapping

---

## Pipeline

```
RequestHandler  →  ResponseHandler  →  PersistenceHandler  →  enrich()
```

| Stage | Shared class | When to override |
|---|---|---|
| Request | `HttpGetRequestHandler`, `WebSearchRequestHandler` | When source needs custom auth, pagination, or parsing |
| Response | `ArticleQueueResponseHandler` | When source columns don't map cleanly (e.g. AEMO zip/CSV) |
| Persistence | `ArticleQueuePersistenceHandler` | Rarely — use `InMemoryPersistenceHandler` for dry runs |

---

## Existing runners

### `web/gas_web`
- **Source:** Perplexity `sonar-pro` web search
- **Request handler:** `WebSearchRequestHandler` (shared)
- **Topic:** Single GAS_MARKET prompt, global scope
- **tree_level_2:** Natural Gas

### `db/aemo`
- **Source:** AEMO NEM web zip (GasBBActualFlowStorage.csv)
- **Request handler:** `HttpGetRequestHandler` (shared)
- **Response handler:** `AemoResponseHandler` (custom — unpacks zip, parses CSV)
- **tree_level_2:** LNG

---

## Adding a new DB / API runner

1. Create `runners/db/<name>/`
2. Add `appsettings.py`:
   ```python
   from appsettings import *
   SOURCE_TYPE  = "database"   # or "api"
   SOURCE_NAME  = "my_source"
   TREE_LEVEL_2 = "Natural Gas"
   ```
3. Add `run.py`:
   ```python
   import os, sys, logging, traceback
   from time import time
   sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
   from dotenv import load_dotenv; load_dotenv()
   import runners.db.<name>.appsettings as settings
   from scraper.request.request_handler import RequestHandler
   from scraper.response.article_queue_response_handler import ArticleQueueResponseHandler
   from scraper.persistence.article_queue_persistence_handler import ArticleQueuePersistenceHandler
   from scraper.scraper import Scraper
   from scraper.enrichment import enrich

   class MyRequestHandler(RequestHandler):
       def handle(self, **kwargs) -> list[dict]:
           # query DB / call API, return list of row dicts
           return [{"Id": "...", "Title": "...", "Body": "...", ...}]

   def run():
       Scraper(
           request_handler=MyRequestHandler(),
           response_handler=ArticleQueueResponseHandler(
               source_type=settings.SOURCE_TYPE,
               source_name=settings.SOURCE_NAME,
               tree_level_2=settings.TREE_LEVEL_2,
           ),
           persistence_handler=ArticleQueuePersistenceHandler(),
       ).scrape()
       enrich()
   ```
4. Add a DAG in `airflow/dags/<name>_dag.py`

---

## Adding a new web runner

Same as above but in `runners/web/<name>/` and use `WebSearchRequestHandler` instead of a custom request handler. Set prompts in a `prompts.py` file.
