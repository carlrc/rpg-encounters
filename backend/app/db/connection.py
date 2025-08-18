import os

from dotenv import load_dotenv
from sqlalchemy import create_engine

# Load environment variables from .env file
load_dotenv()

USERS_TABLE = "users"
PLAYERS_TABLE = "players"
CHARACTERS_TABLE = "characters"
MEMORIES_TABLE = "memories"
REVEALS_TABLE = "reveals"
INFLUENCES_TABLE = "influences"
ENCOUNTERS_TABLE = "encounters"
CONNECTIONS_TABLE = "connections"
WORLDS_TABLE = "worlds"

# Database URLs
DATABASE_URL = os.getenv("DATABASE_URL")


def get_db_engine():
    """Get database engine, defaulting to test database for safety

    Args:
        use_test_db: If True, use test database. If False, use live database.

    Returns:
        SQLAlchemy engine instance
    """
    if not DATABASE_URL:
        raise ValueError("DATABASE_URL not set in env")
    return create_engine(DATABASE_URL)
