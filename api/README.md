# Part 8 - API + Frontend Service

This package is the **separate API/frontend service** that sits on top of the
`Articles` and `ArticleLikes` tables.

## Included
- FastAPI app
- Jinja2 templates
- static CSS + JS
- article feed API
- article detail API
- like / unlike / like-status APIs
- HTML pages:
  - `/`
  - `/feed`
  - `/articles/{article_id}`
- auth placeholder dependency
- SQLite demo DB with seed data

## Pages
- `/feed` -> article feed
- `/articles/{article_id}` -> article detail

## APIs
- `GET /api/articles`
- `GET /api/articles/{article_id}`
- `POST /api/articles/{article_id}/like`
- `DELETE /api/articles/{article_id}/like`
- `GET /api/articles/{article_id}/like-status`

## Run
```bash
pip install -r requirements.txt
python seed_data.py
uvicorn main:app --reload
```

Then open:
- http://127.0.0.1:8000/feed

## Notes
- auth is still a placeholder in this part
- merge with Part 1 for Ping auth
- replace SQLite with your shared SQL Server DB later
