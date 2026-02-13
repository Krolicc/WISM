from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from backend.api import story

from pathlib import Path

# This builds a robust path to the .env file, which is located in the project root
# (one level up from the 'backend' directory where this config.py file is).
# Path(__file__) -> .../backend/config.py
# .parent        -> .../backend/
# .parent        -> .../ (project root)
# / ".env"       -> .../.env
frontend_directory_path = Path(__file__).parent.parent / "frontend"

app = FastAPI(
    title="Comics Generation Service",
    description="An orchestrator for generating comics using AI.",
    version="0.1.0",
)

# --- Include API Routers ---
app.include_router(story.router, prefix="/api/v1", tags=["Story Generation"])

# --- Mount Static files for frontend ---
app.mount("/", StaticFiles(directory=frontend_directory_path, html=True), name="static")
