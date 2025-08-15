from app.db.connection import DB_ENGINE
from app.db.models.base import UnifiedCharacterBase
from app.db.models.character import CharacterORM
from app.db.models.memory import MemoryORM
from app.db.models.player import Base as PlayerORM
from app.db.models.reveal import RevealORM


def create_tables():
    """Create all database tables"""
    PlayerORM.metadata.create_all(bind=DB_ENGINE)
    CharacterORM.metadata.create_all(bind=DB_ENGINE)
    MemoryORM.metadata.create_all(bind=DB_ENGINE)
    RevealORM.metadata.create_all(bind=DB_ENGINE)
    UnifiedCharacterBase.metadata.create_all(bind=DB_ENGINE)


def drop_tables():
    """Drop all database tables"""
    PlayerORM.metadata.drop_all(bind=DB_ENGINE)
    CharacterORM.metadata.drop_all(bind=DB_ENGINE)
    MemoryORM.metadata.drop_all(bind=DB_ENGINE)
    RevealORM.metadata.drop_all(bind=DB_ENGINE)
    UnifiedCharacterBase.metadata.drop_all(bind=DB_ENGINE)


if __name__ == "__main__":
    create_tables()
