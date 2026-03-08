import logging
from typing import List

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.data.base_store import BaseStore
from app.db.models.player import PlayerORM
from app.models.player import Player, PlayerCreate, PlayerUpdate

logger = logging.getLogger(__name__)


class PlayerStore(BaseStore):
    def __init__(
        self,
        user_id: int,
        world_id: int,
        session: AsyncSession | None = None,
    ):
        super().__init__(user_id=user_id, world_id=world_id, session=session)

    async def get_all(self) -> List[Player]:
        """Get all players for the current user and world"""
        try:
            async with self.get_session() as session:
                result = await session.execute(
                    select(PlayerORM).where(
                        PlayerORM.user_id == self.user_id,
                        PlayerORM.world_id == self.world_id,
                    )
                )
                player_orms = result.scalars().all()
                return [Player.model_validate(player_orm) for player_orm in player_orms]
        except SQLAlchemyError as e:
            logger.error(
                f"Error in get_all for user {self.user_id}, world {self.world_id}: {e}"
            )
            raise

    async def get_by_id(self, player_id: int) -> Player | None:
        """Get a specific player by ID for the current user and world"""
        try:
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
        except SQLAlchemyError as e:
            logger.error(
                f"Error in get_by_id for user {self.user_id}, world {self.world_id}, player {player_id}: {e}"
            )
            raise

    async def create(self, player_data: PlayerCreate) -> Player:
        """Create a new player"""
        try:
            async with self.get_session() as session:
                player_orm = PlayerORM(
                    **player_data.model_dump(),
                    user_id=self.user_id,
                    world_id=self.world_id,
                )
                session.add(player_orm)
                await session.flush()
                await session.refresh(player_orm)
                return Player.model_validate(player_orm)
        except SQLAlchemyError as e:
            logger.error(
                f"Error in create for user {self.user_id}, world {self.world_id}: {e}"
            )
            raise

    async def update(
        self, player_id: int, player_update: PlayerUpdate
    ) -> Player | None:
        """Update an existing player for the current user and world"""
        try:
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
        except SQLAlchemyError as e:
            logger.error(
                f"Error in update for user {self.user_id}, world {self.world_id}, player {player_id}: {e}"
            )
            raise

    async def delete(self, player_id: int) -> bool:
        """Delete a player for the current user and world"""
        try:
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
        except SQLAlchemyError as e:
            logger.error(
                f"Error in delete for user {self.user_id}, world {self.world_id}, player {player_id}: {e}"
            )
            raise

    async def exists(self, player_id: int) -> bool:
        """Check if a player exists for the current user and world"""
        try:
            async with self.get_session() as session:
                result = await session.execute(
                    select(PlayerORM).where(
                        PlayerORM.id == player_id,
                        PlayerORM.user_id == self.user_id,
                        PlayerORM.world_id == self.world_id,
                    )
                )
                return result.scalars().first() is not None
        except SQLAlchemyError as e:
            logger.error(
                f"Error in exists for user {self.user_id}, world {self.world_id}, player {player_id}: {e}"
            )
            raise
