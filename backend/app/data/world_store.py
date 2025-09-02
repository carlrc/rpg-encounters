from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.data.base_store import BaseStore
from app.db.models.world import WorldORM
from app.models.world import World


class WorldStore(BaseStore):
    def __init__(self, user_id: int, session: AsyncSession = None):
        # WorldStore has user_id but no world_id, so we pass None for world_id
        super().__init__(user_id=user_id, world_id=None, session=session)

    async def get_all_worlds(self) -> List[World]:
        """Get all worlds for the current user"""
        async with self.get_session() as session:
            result = await session.execute(
                select(WorldORM)
                .where(WorldORM.user_id == self.user_id)
                .order_by(WorldORM.created_at)
            )
            world_orms = result.scalars().all()
            return [World.model_validate(world_orm) for world_orm in world_orms]

    async def get_world_by_id(self, world_id: int) -> World | None:
        """Get a specific world by ID for the current user"""
        async with self.get_session() as session:
            result = await session.execute(
                select(WorldORM).where(
                    WorldORM.id == world_id, WorldORM.user_id == self.user_id
                )
            )
            world_orm = result.scalars().first()
            if world_orm:
                return World.model_validate(world_orm)
            return None

    async def create_world(self) -> World:
        """Create a new world for the current user"""
        async with self.get_session() as session:
            # Create world with just user_id, other fields are auto-generated
            world_orm = WorldORM(user_id=self.user_id)
            session.add(world_orm)
            await session.flush()
            await session.refresh(world_orm)
            return World.model_validate(world_orm)

    async def delete_world(self, world_id: int) -> bool:
        """Delete a world for the current user"""
        async with self.get_session() as session:
            result = await session.execute(
                select(WorldORM).where(
                    WorldORM.id == world_id, WorldORM.user_id == self.user_id
                )
            )
            world_orm = result.scalars().first()
            if not world_orm:
                return False

            await session.delete(world_orm)
            return True

    async def world_exists(self, world_id: int) -> bool:
        """Check if a world exists for the current user"""
        async with self.get_session() as session:
            result = await session.execute(
                select(WorldORM).where(
                    WorldORM.id == world_id, WorldORM.user_id == self.user_id
                )
            )
            return result.scalars().first() is not None
