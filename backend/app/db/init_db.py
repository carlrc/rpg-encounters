from app.db.connection import get_db_engine
from app.db.models.base import UnifiedBase


def create_tables(use_test_db=True):
    """Create all database tables"""

    engine = get_db_engine(use_test_db)
    UnifiedBase.metadata.create_all(bind=engine)


def drop_tables(use_test_db=True):
    """Drop all database tables"""

    engine = get_db_engine(use_test_db)
    UnifiedBase.metadata.drop_all(bind=engine)


if __name__ == "__main__":
    create_tables(use_test_db=True)
