from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.connection import get_async_db_session


class BaseStore:
    def __init__(
        self,
        user_id: int | None,
        world_id: int | None = None,
        session: AsyncSession | None = None,
    ):
        self.user_id = user_id
        self.world_id = world_id
        self.session = session

    @asynccontextmanager
    async def get_session(self):
        """Get an async database session - either the shared one or create one"""
        if self.session:
            yield self.session
        else:
            async with get_async_db_session() as session:
                yield session
