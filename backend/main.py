from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from backend.api import story

app = FastAPI(
    title="Comics Generation Service",
    description="An orchestrator for generating comics using AI.",
    version="0.1.0",
)

# --- Include API Routers ---
app.include_router(story.router, prefix="/api/v1", tags=["Story Generation"])

# --- Mount Static files for frontend ---
app.mount("/", StaticFiles(directory="frontend", html=True), name="static")
