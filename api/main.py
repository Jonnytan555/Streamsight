from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.api import articles, auth, likes

import uvicorn


BASE_DIR = Path(__file__).resolve().parent
FRONTEND_DIST = (BASE_DIR / ".." / "frontend" / "dist").resolve()

if not FRONTEND_DIST.exists():
    raise RuntimeError(f"Frontend build not found at: {FRONTEND_DIST}")

if not (FRONTEND_DIST / "index.html").exists():
    raise RuntimeError("index.html missing from frontend build")

app = FastAPI(title="Commodity News Tracker API")

# Routers
app.include_router(articles.router)
app.include_router(likes.router)
app.include_router(auth.router)

# Static assets (JS, CSS)
app.mount(
    "/assets",
    StaticFiles(directory=str(FRONTEND_DIST / "assets")),
    name="assets",
)

INDEX_FILE = FRONTEND_DIST / "index.html"


@app.get("/", include_in_schema=False)
def serve_root():
    return FileResponse(INDEX_FILE)


@app.get("/{full_path:path}", include_in_schema=False)
def serve_spa(full_path: str):
    if full_path.startswith(("api", "docs", "redoc", "openapi.json", "assets")):
        raise HTTPException(status_code=404, detail="Not found")

    return FileResponse(INDEX_FILE)


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)