from __future__ import annotations

from contextlib import asynccontextmanager
from functools import wraps
from typing import AsyncGenerator

from llms.models import *  # noqa: F403
from messages.models import *  # noqa: F403
from settings import Settings, settings
from sqlalchemy.ext.asyncio import (
    AsyncConnection,
    AsyncEngine,
    AsyncSession,
    create_async_engine,
)
from sqlalchemy.orm import sessionmaker

from users.models import *  # noqa: F403


async def get_engine(settings: Settings) -> AsyncEngine:
    engine = create_async_engine(
        settings.get_db_str(),
        connect_args=settings.build_connect_args(),
        future=True,
    )
    return engine


@asynccontextmanager
async def get_connection(engine: AsyncEngine) -> AsyncGenerator[AsyncConnection, None]:
    async with engine.connect() as conn:
        yield conn


@asynccontextmanager
async def get_session(engine: AsyncEngine) -> AsyncGenerator[AsyncSession, None]:
    AsyncSessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

    async with AsyncSessionLocal() as session:
        async with session.begin():
            yield session


def atomic(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        engine = await get_engine(settings)
        try:
            async with get_session(engine) as session:
                return await func(session, *args, **kwargs)
        finally:
            await engine.dispose()

    return wrapper
