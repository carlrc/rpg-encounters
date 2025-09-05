import logging
import os
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

load_dotenv()

logger = logging.getLogger(__name__)

USERS_TABLE = "users"
ACCOUNTS_TABLE = "accounts"
MODERATIONS_TABLE = "moderations"
PLAYERS_TABLE = "players"
CHARACTERS_TABLE = "characters"
MEMORIES_TABLE = "memories"
REVEALS_TABLE = "reveals"
INFLUENCES_TABLE = "influences"
ENCOUNTERS_TABLE = "encounters"
CONNECTIONS_TABLE = "connections"
WORLDS_TABLE = "worlds"
CONVERSATIONS_TABLE = "conversations"

DATABASE_URL = os.getenv("DATABASE_URL")


def get_async_db_engine():
    """Get database engine, defaulting to test database for safety"""
    if not DATABASE_URL:
        raise ValueError("DATABASE_URL not set in env")
    # https://docs.sqlalchemy.org/en/20/core/pooling.html
    return create_async_engine(DATABASE_URL, pool_size=0)


# FastAPI dependency for routes
async def get_async_db_routes_session() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency that provides async session for route handlers"""
    # Async session factory
    AsyncSessionLocal = async_sessionmaker(
        bind=get_async_db_engine(), class_=AsyncSession, expire_on_commit=False
    )
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            logger.error(f"Rolling back transaction. {e}")
            await session.rollback()
            raise
        finally:
            await session.close()


# Async context manager for services
@asynccontextmanager
async def get_async_db_session(db_url: str = None):
    """Creates an async context with proper transaction management."""
    engine = create_async_engine(db_url) if db_url else get_async_db_engine()
    async_session = async_sessionmaker(
        bind=engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            logger.error(f"Rolling back transaction. {e}")
            await session.rollback()
            raise
        finally:
            await session.close()
