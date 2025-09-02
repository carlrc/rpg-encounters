import asyncio
import sys

from sqlalchemy.ext.asyncio import AsyncEngine

from app.db.connection import get_async_db_engine

# Import association tables to ensure they are registered with SQLAlchemy
from app.db.models.associations import (  # noqa: F401
    encounter_characters,
    memory_characters,
    reveal_characters,
)
from app.db.models.base import SimpleBase, UnifiedBase
from app.db.models.character import CharacterORM  # noqa: F401
from app.db.models.connection import ConnectionORM  # noqa: F401
from app.db.models.conversation import ConversationORM  # noqa: F401
from app.db.models.encounter import EncounterORM  # noqa: F401
from app.db.models.influence import InfluenceORM  # noqa: F401
from app.db.models.memory import MemoryORM  # noqa: F401
from app.db.models.player import PlayerORM  # noqa: F401
from app.db.models.reveal import RevealORM  # noqa: F401

# Import all ORM models to ensure they are registered with SQLAlchemy
# This is necessary for SQLAlchemy to know about all tables and their relationships
from app.db.models.user import UserORM  # noqa: F401
from app.db.models.world import WorldORM  # noqa: F401


async def create_tables(engine: AsyncEngine):
    """Create all database tables asynchronously"""
    async with engine.begin() as conn:
        await conn.run_sync(SimpleBase.metadata.create_all)
        await conn.run_sync(UnifiedBase.metadata.create_all)


async def drop_tables(engine: AsyncEngine):
    """Drop all database tables asynchronously"""
    async with engine.begin() as conn:
        await conn.run_sync(UnifiedBase.metadata.drop_all)
        await conn.run_sync(SimpleBase.metadata.drop_all)


async def main():
    engine = get_async_db_engine()

    if "--drop" in sys.argv:
        print("🔴 Dropping tables...")
        await drop_tables(engine)
    else:
        print("🟢 Creating tables...")
        await create_tables(engine)


if __name__ == "__main__":
    asyncio.run(main())
