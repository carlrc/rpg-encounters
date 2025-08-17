from app.db.connection import DB_ENGINE
from app.db.models.base import UnifiedBase


def create_tables():
    """Create all database tables"""
    UnifiedBase.metadata.create_all(bind=DB_ENGINE)


def drop_tables():
    """Drop all database tables"""
    UnifiedBase.metadata.drop_all(bind=DB_ENGINE)


if __name__ == "__main__":
    create_tables()
