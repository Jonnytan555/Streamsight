# Streamsight

Commodity news intelligence platform. Ingests articles from web search and internal databases, enriches them with LLM summaries and commodity taxonomy, then serves them via a FastAPI + React frontend.

---

## How it works

```
Web search (Perplexity)  ──►  article_queue  ──►  ArticleSummariser (Claude)  ──►  articles
DB tables (ENTSOG etc.)  ──►  article_queue  ──►  ArticleSummariser (Claude)  ──►  articles
                                                                                      ↓
                                                                               FastAPI + React
```

All pipeline components are injectable — swap real dependencies for test doubles without changing pipeline code.

---

## Project structure

```
articles/
  article_pipeline.py         Core orchestrator: reader → enricher → writer
  enrich/
    queue_reader.py           Reads pending rows from article_queue
    article_summariser.py     Calls summariser, tracks LLM cost
    article_writer.py         Writes enriched articles to articles table
    web/
      claude_summariser.py    LLM summariser via Anthropic API
      web_tree_slicer.py      Scopes commodity tree to article context
    db/
      concat_summariser.py    Passthrough summariser (no LLM cost)
  queue/
    queue_writer.py           Writes mapped rows to article_queue
    source_queuer.py          Orchestrates DB table → article_queue
    db/
      db_table_reader.py      Reads rows from an external DB table
      column_mapper.py        Maps external schema → article_queue shape
    web/
      search_result_mapper.py Maps web search results → article_queue shape

runners/
  web/
    gas_web/                  Perplexity search → European/US/Asian gas articles
    oil_web/                  Perplexity search → crude oil articles
    ags_web/                  Perplexity search → agricultural commodity articles
  db/
    ensog/                    ENTSOG Urgent Market Messages → articles
    archive/aemo/             AEMO gas flow data (archived)

api/                          FastAPI service — articles feed, likes, auth
frontend/                     React frontend

scheduling/
  airflow/dags/               Airflow DAGs (one per runner)
  cron/streamsight             Linux cron schedule (direct server install)
  windows/                    Windows Task Scheduler .bat files

utils/tracking/
  llm_usage_tracker.py        Records LLM token usage and cost to DB
  budget_checker.py           Raises if daily LLM spend limit exceeded
  domain_tracker.py           Blocks domains with zero results

sql/                          Table DDL scripts
tests/                        Unit and integration tests
```

---

## Running locally

**1. Install dependencies**
```bash
pip install -r requirements.txt
```

**2. Configure environment**
```bash
cp .env.example .env
# Set PERPLEXITY_API_KEY and ANTHROPIC_API_KEY
```

**3. Run a web runner**
```bash
python -m runners.web.gas_web.run
python -m runners.web.oil_web.run
python -m runners.web.ags_web.run
```

**4. Run a DB runner**
```bash
python -m runners.db.ensog.run
```

---

## Running with Docker

```bash
# Start API + frontend + runners (all-in-one)
docker compose up --build
```

- **api** — FastAPI + React at `http://localhost:8000`
- **runners** — cron-based, fires on schedule (see `crontab`)

---

## API + frontend only (server deployment)

```bash
docker compose up api
```

Or use the API-only profile for a remote server where runners run elsewhere.

---

## Scheduling

| Method | Where | Files |
|---|---|---|
| Docker cron | Inside runners container | `crontab` |
| Linux cron | Direct server install | `scheduling/cron/streamsight` |
| Windows Task Scheduler | Local Windows machine | `scheduling/windows/*.bat` |
| Airflow | Managed Airflow | `scheduling/airflow/dags/` |

Set `APP_ROOT` env var to the repo path when using Airflow or Linux cron directly.

---

## Environment variables

| Variable | Description | Default |
|---|---|---|
| `DB_SERVER` | SQL Server hostname | `localhost` |
| `DB_NAME` | Main database name | `STREAMSIGHT` |
| `DB_USER` | SQL login (required for Docker) | Windows auth |
| `DB_PASS` | SQL password | — |
| `SCRAPE_DB_SERVER` | WebScrapes DB hostname (if different) | same as `DB_SERVER` |
| `PERPLEXITY_API_KEY` | Perplexity API key for web search | — |
| `ANTHROPIC_API_KEY` | Anthropic API key for Claude | — |
| `APP_ROOT` | Repo root path (Airflow/cron) | `/app` |

---

## LLM cost guard

Each runner checks rolling 24-hour LLM spend before running. Raises if the limit is exceeded.

```bash
MAX_DAILY_LLM_SPEND_USD=1.0   # set in appsettings.py
```

---

## Tests

```bash
pytest -v
```

Unit tests cover pipeline orchestration, column mapping, summarisation, and tree slicing.
Integration tests use SQLite with mocked SQL Server operations.
