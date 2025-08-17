import os

from dotenv import load_dotenv
from sqlalchemy import create_engine

# Load environment variables from .env file
load_dotenv()

PLAYERS_TABLE = "players"
CHARACTERS_TABLE = "characters"
MEMORIES_TABLE = "memories"
REVEALS_TABLE = "reveals"
INFLUENCES_TABLE = "influences"
ENCOUNTERS_TABLE = "encounters"
CONNECTIONS_TABLE = "connections"

# Database URLs
DATABASE_URL = os.getenv("DATABASE_URL")
TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL")


def get_db_engine(use_test_db=True):
    """Get database engine, defaulting to test database for safety

    Args:
        use_test_db: If True, use test database. If False, use production database.

    Returns:
        SQLAlchemy engine instance
    """
    if use_test_db:
        if not TEST_DATABASE_URL:
            raise ValueError(
                "TEST_DATABASE_URL not configured in environment variables"
            )
        return create_engine(TEST_DATABASE_URL)
    if not DATABASE_URL:
        raise ValueError("DATABASE_URL not configured in environment variables")
    return create_engine(DATABASE_URL)


# Default to production database for backward compatibility
# Individual modules can override this by calling get_db_engine(use_test_db=True)
DB_ENGINE = create_engine(DATABASE_URL) if DATABASE_URL else None
