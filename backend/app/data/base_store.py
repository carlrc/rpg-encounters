from contextlib import contextmanager
from typing import Optional

from sqlalchemy import Engine
from sqlalchemy.orm import Session, sessionmaker

from app.db.connection import get_db_engine


class BaseStore:
    def __init__(
        self,
        user_id: int,
        world_id: int | None = None,
        engine: Engine = get_db_engine(),
        session: Optional[Session] = None,
    ):
        self.user_id = user_id
        self.world_id = world_id
        self.session = session
        self.Session = sessionmaker(engine) if not session else None

    @contextmanager
    def get_session(self):
        """Get a database session - either the shared one or create a new one"""
        if self.session:
            # If we have a shared session, just yield it (no commit/rollback)
            yield self.session
        else:
            # Create a new session with proper transaction handling
            with self.Session() as session:
                yield session
