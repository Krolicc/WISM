import uvicorn
from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware

from app.api.api import api_router
from app.database import db_helper

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    yield
    # Shutdown
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

app.include_router(api_router, prefix="/api/v1")

if __name__ == "__main__":
    # Note: Use `uvicorn app.main:app --reload` in the terminal for development
    uvicorn.run(app, host="0.0.0.0", port=8000)
