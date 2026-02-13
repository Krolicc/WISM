from fastapi import FastAPI
from app.api.api import api_router
from app.database import engine, Base

# Create all tables in the database.
# This is a good place to do it, as it will be executed once when the app starts.
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Comic Book API",
    description="An API for creating and managing comic book stories, characters, scenes, and panels.",
    version="0.1.0",
)

app.include_router(api_router, prefix="/api/v1")

@app.get("/", tags=["Root"])
async def read_root():
    return {"message": "Welcome to the Comic Book API"}
