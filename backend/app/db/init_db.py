from app.db.connection import DB_ENGINE
from app.db.models.base import CharacterMemoryBase
from app.db.models.player import Base as PlayerBase


def create_tables():
    """Create all database tables"""
    PlayerBase.metadata.create_all(bind=DB_ENGINE)
    CharacterMemoryBase.metadata.create_all(bind=DB_ENGINE)


def drop_tables():
    """Drop all database tables"""
    PlayerBase.metadata.drop_all(bind=DB_ENGINE)
    CharacterMemoryBase.metadata.drop_all(bind=DB_ENGINE)


if __name__ == "__main__":
    create_tables()
