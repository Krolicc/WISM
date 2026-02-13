
import os
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base

# Define the database URL. We'll use SQLite for simplicity.
# The database file will be created in the backend directory.
DATABASE_URL = "sqlite+aiosqlite:///./wism.db"

# Create the SQLAlchemy engine for asynchronous operation
engine = create_async_engine(DATABASE_URL)

# Create a configured "Session" class for async sessions
SessionLocal = sessionmaker(
    autocommit=False, 
    autoflush=False, 
    bind=engine,
    class_=AsyncSession
)

# Create a base class for our models
Base = declarative_base()

# Dependency to get a DB session
async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as session:
        yield session
