from sqlalchemy import Engine

from app.db.connection import get_db_engine

# Import association tables to ensure they are registered with SQLAlchemy
from app.db.models.associations import (  # noqa: F401
    encounter_characters,
    memory_characters,
    reveal_characters,
)
from app.db.models.base import SimpleBase, UnifiedBase
from app.db.models.character import CharacterORM  # noqa: F401
from app.db.models.connection import ConnectionORM  # noqa: F401
from app.db.models.encounter import EncounterORM  # noqa: F401
from app.db.models.influence import InfluenceORM  # noqa: F401
from app.db.models.memory import MemoryORM  # noqa: F401
from app.db.models.player import PlayerORM  # noqa: F401
from app.db.models.reveal import RevealORM  # noqa: F401

# Import all ORM models to ensure they are registered with SQLAlchemy
# This is necessary for SQLAlchemy to know about all tables and their relationships
from app.db.models.user import UserORM  # noqa: F401
from app.db.models.world import WorldORM  # noqa: F401


def create_tables(engine: Engine):
    """Create all database tables"""
    SimpleBase.metadata.create_all(bind=engine)
    UnifiedBase.metadata.create_all(bind=engine)


def drop_tables(engine: Engine):
    """Drop all database tables"""
    UnifiedBase.metadata.drop_all(bind=engine)
    SimpleBase.metadata.drop_all(bind=engine)


if __name__ == "__main__":
    create_tables(get_db_engine())
