import asyncio
import uvicorn
from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware

from app.core.database import db_helper
from app.core.celery_app import celery_app
from app.endpoints import api_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Application starting up...")
    yield
    # Shutdown
    print("Application shutting down...")

    await db_helper.dispose()

app = FastAPI(
    lifespan=lifespan,
    title="Comic Book API",
    description="An API for creating and managing comic book stories, characters, scenes, and panels.",
    version="0.1.0",
)

# Define the specific origin of your frontend application.
# This is more secure than allowing all origins with "*".
origins = [
    "https://5173-firebase-wism-1770010266998.cluster-4cmpbiopffe5oqk7tloeb2ltrk.cloudworkstations.dev",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

app.include_router(api_router, prefix='/api/v1')

# The celery_app object must be in the same module as the app object for the worker to find it.
# We are exposing the celery_app imported from core to be discoverable by the celery worker command.
__all__ = ('celery_app',)

if __name__ == "__main__":
    # Note: Use `uvicorn app.main:app --reload` in the terminal for development
    uvicorn.run(app, host="0.0.0.0", port=8002)
