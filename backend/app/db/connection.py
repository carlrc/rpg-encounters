import logging
import os
from contextlib import contextmanager

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

load_dotenv()

logger = logging.getLogger(__name__)

USERS_TABLE = "users"
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


def get_db_engine():
    """Get database engine, defaulting to test database for safety"""
    if not DATABASE_URL:
        raise ValueError("DATABASE_URL not set in env")
    return create_engine(DATABASE_URL)


@contextmanager
def get_db_session(db_url: str = None):
    """Creates a context with an open SQLAlchemy session with proper transaction management."""

    engine = create_engine(db_url) if db_url else get_db_engine()
    db_session = scoped_session(sessionmaker(bind=engine))

    try:
        yield db_session
        db_session.commit()
    except Exception as e:
        logger.error(f"Rolling back transaction. {e}")
        db_session.rollback()
        raise
    finally:
        db_session.close()
