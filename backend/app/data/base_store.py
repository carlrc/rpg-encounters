from contextlib import contextmanager

from sqlalchemy import Engine
from sqlalchemy.orm import Session, sessionmaker

from app.db.connection import get_db_engine, get_db_session


class BaseStore:
    def __init__(
        self,
        user_id: int,
        world_id: int | None = None,
        engine: Engine = get_db_engine(),
        session: Session | None = None,
    ):
        self.user_id = user_id
        self.world_id = world_id
        self.session = session
        self.Session = sessionmaker(engine) if not session else None

    @contextmanager
    def get_session(self):
        """Get a database session - either the shared one or create one"""
        if self.session:
            yield self.session
        else:
            with get_db_session() as session:
                yield session
