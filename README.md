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

## Database setup

### Docker (recommended)

Schema is created automatically on first boot — no manual steps needed. See [DEPLOYMENT.md](DEPLOYMENT.md).

### Local SQL Server

Create a `STREAMSIGHT` database in SQL Server (SSMS), then run these scripts **in order**:

```
sql/ingestion/article_queue.sql
sql/ingestion/articles.sql
sql/api/users.sql
sql/api/article_likes.sql
sql/tracking/llm_usage.sql
sql/tracking/blocked_domains.sql
sql/taxonomy/commodity_tree.sql   ← run last (references articles table)
```

### ENSOG DB runner

The ENSOG runner reads from a separate `Scrape` SQL Server database. You need access to a server containing the `ENTSOGUrgentMarketMessages` table. If you don't have this, skip the ENSOG runner — the web runners work independently.

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
# Or set DEMO_MODE=true to test without API keys (see below)
```

**3. Run a web runner**
```bash
python -m runners.web.gas_web.run
python -m runners.web.oil_web.run
python -m runners.web.ags_web.run
```

**4. Run the ENSOG DB runner** *(requires access to Scrape DB)*
```bash
python -m runners.db.ensog.run
```

### Testing without API keys (demo mode)

Set `DEMO_MODE=true` in your `.env`. The pipeline runs end-to-end but skips Claude and Perplexity — articles are written using the raw body text as the summary. No API keys required.

---

## Running with Docker

```bash
docker compose up -d --build
```

Four services start automatically:

| Service | Description |
|---|---|
| `db` | SQL Server 2022 (persisted volume) |
| `db-init` | Creates schema on first boot, then exits |
| `api` | FastAPI + React at `http://localhost:8000` |
| `runners` | Cron-scheduled pipeline jobs |

For full server deployment instructions see [DEPLOYMENT.md](DEPLOYMENT.md).

---

## Scheduling

| Method | Where | Files |
|---|---|---|
| Docker cron | Inside runners container | `crontab` |
| Linux cron | Direct server install | `scheduling/cron/streamsight` |
| Windows Task Scheduler | Local Windows machine | `scheduling/windows/*.bat` |
| Airflow | Managed Airflow | `scheduling/airflow/dags/` |
| Dagster | Local or server | `scheduling/dagster/definitions.py` |

Set `APP_ROOT` env var to the repo path when using Airflow, Dagster, or Linux cron directly.

### Running with Dagster

```bash
pip install dagster dagster-webserver
dagster dev -f scheduling/dagster/definitions.py
```

Open `http://localhost:3000` — you get a full UI to trigger runs manually, view logs, and enable/disable schedules. All four runners are defined as jobs with 6-hourly schedules.

---

## Environment variables

| Variable | Description | Default |
|---|---|---|
| `DB_SERVER` | SQL Server hostname (local only — Docker sets this automatically) | `localhost` |
| `DB_NAME` | Main database name | `STREAMSIGHT` |
| `DB_USER` | SQL login (local only — Docker uses `sa`) | Windows auth |
| `DB_PASS` | SQL Server password (required for Docker) | — |
| `SCRAPE_DB_SERVER` | WebScrapes DB hostname (if different) | same as `DB_SERVER` |
| `PERPLEXITY_API_KEY` | Perplexity API key for web search | — |
| `ANTHROPIC_API_KEY` | Anthropic API key for Claude | — |
| `DEMO_MODE` | Skip Claude/Perplexity, use raw text as summary | `false` |
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
