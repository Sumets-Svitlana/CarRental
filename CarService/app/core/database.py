from contextlib import asynccontextmanager
from functools import lru_cache
from typing import AsyncIterable

from alembic.config import Config
from pydantic import PostgresDsn
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base

from app.core.config import get_settings

Base = declarative_base()


@lru_cache
def _async_engine() -> AsyncEngine:
    return create_async_engine(
        get_settings().DATABASE_URL.unicode_string(),
        pool_pre_ping=True,
    )


@lru_cache
def _async_session_factory() -> async_sessionmaker:
    return async_sessionmaker(
        bind=_async_engine(),
        autoflush=False,
        expire_on_commit=False,
    )


@asynccontextmanager
async def _get_managed_session():
    factory: async_sessionmaker = _async_session_factory()
    session: AsyncSession = factory()
    try:
        yield session
    except Exception as e:
        await session.rollback()
        raise e
    else:
        await session.commit()
    finally:
        await session.close()


async def get_session() -> AsyncIterable[AsyncSession]:
    async with _get_managed_session() as session:
        yield session


def get_alembic_config(database_url: PostgresDsn, script_location: str = 'migrations') -> Config:
    alembic_config = Config()
    alembic_config.set_main_option('script_location', script_location)
    alembic_config.set_main_option(
        'sqlalchemy.url',
        database_url.unicode_string().replace('postgresql+psycopg', 'postgresql'),
    )
    return alembic_config
