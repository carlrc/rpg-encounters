from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.data.base_store import BaseStore
from app.db.models.player import PlayerORM
from app.models.player import Player, PlayerCreate, PlayerUpdate


class PlayerStore(BaseStore):
    def __init__(
        self,
        user_id: int,
        world_id: int,
        session: AsyncSession = None,
    ):
        super().__init__(user_id=user_id, world_id=world_id, session=session)

    async def get_all(self) -> List[Player]:
        """Get all players for the current user and world"""
        async with self.get_session() as session:
            result = await session.execute(
                select(PlayerORM).where(
                    PlayerORM.user_id == self.user_id,
                    PlayerORM.world_id == self.world_id,
                )
            )
            player_orms = result.scalars().all()
            return [Player.model_validate(player_orm) for player_orm in player_orms]

    async def get_by_id(self, player_id: int) -> Player | None:
        """Get a specific player by ID for the current user and world"""
        async with self.get_session() as session:
            result = await session.execute(
                select(PlayerORM).where(
                    PlayerORM.id == player_id,
                    PlayerORM.user_id == self.user_id,
                    PlayerORM.world_id == self.world_id,
                )
            )
            player_orm = result.scalars().first()
            if player_orm:
                return Player.model_validate(player_orm)
            return None

    async def create(self, player_data: PlayerCreate) -> Player:
        """Create a new player"""
        async with self.get_session() as session:
            player_orm = PlayerORM(
                **player_data.model_dump(), user_id=self.user_id, world_id=self.world_id
            )
            session.add(player_orm)
            await session.flush()
            await session.refresh(player_orm)
            return Player.model_validate(player_orm)

    async def update(
        self, player_id: int, player_update: PlayerUpdate
    ) -> Player | None:
        """Update an existing player for the current user and world"""
        async with self.get_session() as session:
            result = await session.execute(
                select(PlayerORM).where(
                    PlayerORM.id == player_id,
                    PlayerORM.user_id == self.user_id,
                    PlayerORM.world_id == self.world_id,
                )
            )
            player_orm = result.scalars().first()
            if not player_orm:
                return None

            update_data = player_update.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                setattr(player_orm, key, value)

            await session.flush()
            await session.refresh(player_orm)
            return Player.model_validate(player_orm)

    async def delete(self, player_id: int) -> bool:
        """Delete a player for the current user and world"""
        async with self.get_session() as session:
            result = await session.execute(
                select(PlayerORM).where(
                    PlayerORM.id == player_id,
                    PlayerORM.user_id == self.user_id,
                    PlayerORM.world_id == self.world_id,
                )
            )
            player_orm = result.scalars().first()
            if not player_orm:
                return False

            await session.delete(player_orm)
            return True

    async def exists(self, player_id: int) -> bool:
        """Check if a player exists for the current user and world"""
        async with self.get_session() as session:
            result = await session.execute(
                select(PlayerORM).where(
                    PlayerORM.id == player_id,
                    PlayerORM.user_id == self.user_id,
                    PlayerORM.world_id == self.world_id,
                )
            )
            return result.scalars().first() is not None
