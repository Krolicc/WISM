
import os
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base

# Define the database URL. We'll use SQLite for simplicity.
# The database file will be created in the backend directory.
DATABASE_URL = "sqlite+aiosqlite:///./wism.db"

Base = declarative_base()

from asyncio import current_task

from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    async_scoped_session,
    AsyncSession,
)


class DBaseHelper:
    def __init__(
        self,
        url: str,
        echo: bool = False,
        echo_pool: bool = False,
        pool_size: int = 25,
        max_overflow: int = 10,
    ):
        self.engine = create_async_engine(
            url=url,
            echo=echo,
            echo_pool=echo_pool,
            pool_size=pool_size,
            max_overflow=max_overflow,
        )

        self.session_factory = async_sessionmaker(
            bind=self.engine,
            autoflush=False,
            autocommit=False,
            expire_on_commit=False,
        )

    def get_scoped_session(self):
        session = async_scoped_session(
            session_factory=self.session_factory,
            scopefunc=current_task,
        )

        return session

    async def session_getter(self) -> AsyncSession:
        session = self.get_scoped_session()
        yield session
        await session.close()

    async def dispose(self):
        await self.engine.dispose()


db_helper = DBaseHelper(
    url=DATABASE_URL,
    echo=True,
)