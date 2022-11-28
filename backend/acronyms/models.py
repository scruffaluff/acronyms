"""Database models."""


import functools
from typing import AsyncIterator, Literal

from sqlalchemy import (
    CheckConstraint,
    Column,
    Integer,
    orm,
    Unicode,
    UniqueConstraint,
)
from sqlalchemy.ext import asyncio
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession

from acronyms import settings


AcronymColumn = Literal["id", "abbreviation", "description", "phrase"]
registry: orm.registry = orm.registry()


@registry.mapped
class Acronym:
    """SQL model for acronyms table."""

    __tablename__ = "acronyms"
    __table_args__ = (UniqueConstraint("abbreviation", "phrase"),)

    id = Column(Integer, primary_key=True, index=True)
    abbreviation = Column(
        Unicode,
        CheckConstraint("LENGTH(abbreviation) > 0"),
        index=True,
        nullable=False,
    )
    description = Column(Unicode, nullable=True)
    phrase = Column(
        Unicode,
        CheckConstraint("LENGTH(phrase) > 0"),
        index=True,
        nullable=False,
    )


@functools.lru_cache(maxsize=1)
def get_engine() -> AsyncEngine:
    """Create engine for database connection."""
    uri = settings.settings().database
    if uri.scheme == "sqlite":
        return asyncio.create_async_engine(
            uri, connect_args={"check_same_thread": False}, future=True
        )
    else:
        return asyncio.create_async_engine(uri, future=True)


async def get_session() -> AsyncIterator[AsyncSession]:
    """Create database session."""
    # Argument expire_on_commit=False prevents Greenlet environment from
    # expiring after first request.
    async with AsyncSession(get_engine(), expire_on_commit=False) as session:
        # Teardown logic is executed after HTTP response is completed for
        # "yield" statements in FastAPI,
        # https://fastapi.tiangolo.com/tutorial/dependencies/dependencies-with-yield/.
        yield session


async def initialize_database() -> None:
    """Initialize database."""
    async with get_engine().begin() as connection:
        await connection.run_sync(registry.metadata.create_all)
