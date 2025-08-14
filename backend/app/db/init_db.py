from app.db.connection import DB_ENGINE
from app.db.models.player import Base


def create_tables():
    """Create all database tables"""
    Base.metadata.create_all(bind=DB_ENGINE)


def drop_tables():
    """Drop all database tables"""
    Base.metadata.drop_all(bind=DB_ENGINE)


if __name__ == "__main__":
    create_tables()
