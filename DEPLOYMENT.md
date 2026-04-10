# Deployment Guide — DigitalOcean (Docker)

This guide covers deploying Streamsight to a Linux VPS using Docker Compose. SQL Server runs as a container alongside the app — no external database required.

## Requirements

- A VPS with **at least 2GB RAM** (SQL Server requires it)
- Ubuntu 22.04 or later
- A domain name (optional — you can use the raw IP)

---

## 1 — SSH into the server

```bash
ssh root@YOUR_SERVER_IP
```

---

## 2 — Install Docker

```bash
curl -fsSL https://get.docker.com | sh
systemctl enable docker && systemctl start docker
```

Verify:
```bash
docker --version
docker compose version
```

---

## 3 — Clone the repo

```bash
cd /opt
git clone https://github.com/Jonnytan555/Streamsight.git
cd Streamsight
```

---

## 4 — Create `.env`

```bash
nano .env
```

Paste and fill in your values:

```
PERPLEXITY_API_KEY=pplx-...
ANTHROPIC_API_KEY=sk-ant-...
DB_NAME=STREAMSIGHT
DB_PASS=YourStrongPassword1!
```

> **Note:** `DB_SERVER` and `DB_USER` are set automatically by Docker Compose — do not add them here.
>
> **Password rules:** SQL Server requires a strong password (uppercase, lowercase, number, symbol). Avoid `$` in the password — it is treated as a variable by the shell.

Save with `Ctrl+O`, `Enter`, `Ctrl+X`.

---

## 5 — Start the app

```bash
docker compose up -d --build
```

This will:
1. Pull and start SQL Server 2022
2. Wait for SQL Server to be healthy
3. Run all SQL scripts to create the schema (`db-init` container)
4. Build and start the API + frontend on port 8000
5. Build and start the runners container (cron-scheduled)

First build takes ~5 minutes (downloads base images, builds frontend).

---

## 6 — Check everything is running

```bash
docker compose ps
```

All four services should show `running` (or `exited` for `db-init` — that's expected, it runs once then stops).

View API logs:
```bash
docker compose logs -f api
```

Visit `http://YOUR_SERVER_IP:8000` in your browser.

---

## 7 — Updating after a code change

```bash
cd /opt/Streamsight
git pull
docker compose up -d --build
```

---

## Services

| Service | Description | Port |
|---|---|---|
| `db` | SQL Server 2022 | 1433 (internal) |
| `db-init` | Runs SQL scripts on first boot | — |
| `api` | FastAPI + React frontend | 8000 |
| `runners` | Cron-scheduled pipeline jobs | — |

---

## Persistent data

SQL Server data is stored in a Docker volume (`sqldata`). It persists across restarts and rebuilds. To reset the database completely:

```bash
docker compose down -v
docker compose up -d --build
```

---

## Environment variables reference

| Variable | Description |
|---|---|
| `PERPLEXITY_API_KEY` | Perplexity API key for web search |
| `ANTHROPIC_API_KEY` | Anthropic API key for Claude summarisation |
| `DB_NAME` | Database name (default: `STREAMSIGHT`) |
| `DB_PASS` | SA password for SQL Server container |
| `DEMO_MODE` | Set to `true` to skip Claude/Perplexity (no API keys needed) |

---

## Troubleshooting

**Docker daemon not running:**
```bash
systemctl start docker
```

**`db-init` fails or schema not created:**
```bash
docker compose logs db-init
```
Check for SQL errors. Re-run with:
```bash
docker compose up db-init
```

**API can't connect to DB:**
```bash
docker compose logs api
```
SQL Server takes ~30 seconds to start. If the API starts too fast, restart it:
```bash
docker compose restart api
```

**Out of disk space:**
```bash
docker system prune
```
