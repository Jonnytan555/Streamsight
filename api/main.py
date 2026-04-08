import os
import sys

_api_dir     = os.path.dirname(os.path.abspath(__file__))   # .../api/
_project_root = os.path.dirname(_api_dir)                   # .../Streamsight/
sys.path.insert(0, _project_root)   # for appsettings, articles, etc.
sys.path.insert(0, _api_dir)        # for app.api.*, app.services.*, etc.

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.api import articles, auth, likes

app = FastAPI(title="Commodity News Tracker API")

app.include_router(articles.router)
app.include_router(likes.router)
app.include_router(auth.router)

# In production the React app is built to frontend/dist.
# FastAPI serves the static assets and falls back to index.html for any
# unrecognised path so that React's client-side routing works correctly.
_FRONTEND_DIST = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "frontend", "dist")

if os.path.isdir(_FRONTEND_DIST):
    app.mount("/assets", StaticFiles(directory=os.path.join(_FRONTEND_DIST, "assets")), name="assets")

    @app.get("/{full_path:path}", include_in_schema=False)
    def serve_react(full_path: str):
        """Catch-all: return index.html so React Router handles the path."""
        index = os.path.join(_FRONTEND_DIST, "index.html")
        return FileResponse(index)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
