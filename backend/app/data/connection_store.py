from typing import List

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.data.base_store import BaseStore
from app.db.models.connection import ConnectionORM
from app.models.encounter_connection import (
    Connection,
    ConnectionCreate,
    ConnectionUpdate,
)


class ConnectionStore(BaseStore):
    def __init__(
        self,
        user_id: int,
        world_id: int,
        session: AsyncSession = None,
    ):
        super().__init__(user_id=user_id, world_id=world_id, session=session)

    async def get_all_connections(self) -> List[Connection]:
        """Get all connections for the current user and world"""
        async with self.get_session() as session:
            result = await session.execute(
                select(ConnectionORM).where(
                    ConnectionORM.user_id == self.user_id,
                    ConnectionORM.world_id == self.world_id,
                )
            )
            connection_orms = result.scalars().all()
            return [
                Connection.model_validate(connection_orm)
                for connection_orm in connection_orms
            ]

    async def get_connection_by_id(self, connection_id: int) -> Connection | None:
        """Get a specific connection by ID for the current user and world"""
        async with self.get_session() as session:
            result = await session.execute(
                select(ConnectionORM).where(
                    ConnectionORM.id == connection_id,
                    ConnectionORM.user_id == self.user_id,
                    ConnectionORM.world_id == self.world_id,
                )
            )
            connection_orm = result.scalars().first()
            if connection_orm:
                return Connection.model_validate(connection_orm)
            return None

    async def create_connection(self, connection_data: ConnectionCreate) -> Connection:
        """Create a new connection"""
        async with self.get_session() as session:
            connection_dict = connection_data.model_dump()
            connection_orm = ConnectionORM(
                **connection_dict, user_id=self.user_id, world_id=self.world_id
            )
            session.add(connection_orm)
            await session.flush()
            await session.refresh(connection_orm)
            return Connection.model_validate(connection_orm)

    async def update_connection(
        self, connection_id: int, connection_update: ConnectionUpdate
    ) -> Connection | None:
        """Update an existing connection for the current user and world"""
        async with self.get_session() as session:
            result = await session.execute(
                select(ConnectionORM).where(
                    ConnectionORM.id == connection_id,
                    ConnectionORM.user_id == self.user_id,
                    ConnectionORM.world_id == self.world_id,
                )
            )
            connection_orm = result.scalars().first()
            if not connection_orm:
                return None

            # Update fields
            update_data = connection_update.model_dump(
                exclude_unset=True, exclude={"id"}
            )
            for key, value in update_data.items():
                setattr(connection_orm, key, value)

            await session.flush()
            await session.refresh(connection_orm)
            return Connection.model_validate(connection_orm)

    async def delete_connection(self, connection_id: int) -> bool:
        """Delete a connection for the current user and world"""
        async with self.get_session() as session:
            result = await session.execute(
                select(ConnectionORM).where(
                    ConnectionORM.id == connection_id,
                    ConnectionORM.user_id == self.user_id,
                    ConnectionORM.world_id == self.world_id,
                )
            )
            connection_orm = result.scalars().first()
            if not connection_orm:
                return False

            await session.delete(connection_orm)
            return True

    async def get_connections_for_encounter(
        self, encounter_id: int
    ) -> List[Connection]:
        """Get all connections that involve a specific encounter for the current user and world"""
        async with self.get_session() as session:
            result = await session.execute(
                select(ConnectionORM).where(
                    or_(
                        ConnectionORM.source_encounter_id == encounter_id,
                        ConnectionORM.target_encounter_id == encounter_id,
                    ),
                    ConnectionORM.user_id == self.user_id,
                    ConnectionORM.world_id == self.world_id,
                )
            )
            connection_orms = result.scalars().all()
            return [
                Connection.model_validate(connection_orm)
                for connection_orm in connection_orms
            ]

    async def connection_exists(self, connection_id: int) -> bool:
        """Check if a connection exists for the current user and world"""
        async with self.get_session() as session:
            result = await session.execute(
                select(ConnectionORM).where(
                    ConnectionORM.id == connection_id,
                    ConnectionORM.user_id == self.user_id,
                    ConnectionORM.world_id == self.world_id,
                )
            )
            return result.scalars().first() is not None
