import logging
from typing import List

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.data.base_store import BaseStore
from app.db.models.character import CharacterORM
from app.models.character import Character, CharacterCreate, CharacterUpdate

logger = logging.getLogger(__name__)


class CharacterStore(BaseStore):
    def __init__(
        self,
        user_id: int,
        world_id: int,
        session: AsyncSession = None,
    ):
        super().__init__(user_id=user_id, world_id=world_id, session=session)

    async def get_all(self) -> List[Character]:
        """Get all characters for the current user and world"""
        try:
            async with self.get_session() as session:
                result = await session.execute(
                    select(CharacterORM).where(
                        CharacterORM.user_id == self.user_id,
                        CharacterORM.world_id == self.world_id,
                    )
                )
                character_orms = result.scalars().all()
                return [
                    Character.model_validate(character_orm)
                    for character_orm in character_orms
                ]
        except SQLAlchemyError as e:
            logger.error(
                f"Error getting all characters for user {self.user_id}, world {self.world_id}: {e}"
            )
            raise

    async def get_by_id(self, character_id: int) -> Character | None:
        """Get a specific character by ID for the current user and world"""
        try:
            async with self.get_session() as session:
                result = await session.execute(
                    select(CharacterORM).where(
                        CharacterORM.id == character_id,
                        CharacterORM.user_id == self.user_id,
                        CharacterORM.world_id == self.world_id,
                    )
                )
                character_orm = result.scalars().first()
                if character_orm:
                    return Character.model_validate(character_orm)
                return None
        except SQLAlchemyError as e:
            logger.error(
                f"Error getting character {character_id} for user {self.user_id}, world {self.world_id}: {e}"
            )
            raise

    async def create(self, character_data: CharacterCreate) -> Character:
        """Create a new character"""
        try:
            async with self.get_session() as session:
                character_orm = CharacterORM(
                    **character_data.model_dump(),
                    user_id=self.user_id,
                    world_id=self.world_id,
                )
                session.add(character_orm)
                await session.flush()
                await session.refresh(character_orm)
                return Character.model_validate(character_orm)
        except SQLAlchemyError as e:
            logger.error(
                f"Error creating character for user {self.user_id}, world {self.world_id}: {e}"
            )
            raise

    async def update(
        self, character_id: int, character_update: CharacterUpdate
    ) -> Character | None:
        """Update an existing character for the current user and world"""
        try:
            async with self.get_session() as session:
                result = await session.execute(
                    select(CharacterORM).where(
                        CharacterORM.id == character_id,
                        CharacterORM.user_id == self.user_id,
                        CharacterORM.world_id == self.world_id,
                    )
                )
                character_orm = result.scalars().first()
                if not character_orm:
                    return None

                update_data = character_update.model_dump(exclude_unset=True)
                for key, value in update_data.items():
                    setattr(character_orm, key, value)

                await session.flush()
                await session.refresh(character_orm)
                return Character.model_validate(character_orm)
        except SQLAlchemyError as e:
            logger.error(
                f"Error updating character {character_id} for user {self.user_id}, world {self.world_id}: {e}"
            )
            raise

    async def delete(self, character_id: int) -> bool:
        """Delete a character for the current user and world"""
        try:
            async with self.get_session() as session:
                result = await session.execute(
                    select(CharacterORM).where(
                        CharacterORM.id == character_id,
                        CharacterORM.user_id == self.user_id,
                        CharacterORM.world_id == self.world_id,
                    )
                )
                character_orm = result.scalars().first()
                if not character_orm:
                    return False

                await session.delete(character_orm)
                return True
        except SQLAlchemyError as e:
            logger.error(
                f"Error deleting character {character_id} for user {self.user_id}, world {self.world_id}: {e}"
            )
            raise

    async def exists(self, character_id: int) -> bool:
        """Check if a character exists for the current user and world"""
        try:
            async with self.get_session() as session:
                result = await session.execute(
                    select(CharacterORM).where(
                        CharacterORM.id == character_id,
                        CharacterORM.user_id == self.user_id,
                        CharacterORM.world_id == self.world_id,
                    )
                )
                return result.scalars().first() is not None
        except SQLAlchemyError as e:
            logger.error(
                f"Error checking if character {character_id} exists for user {self.user_id}, world {self.world_id}: {e}"
            )
            raise
