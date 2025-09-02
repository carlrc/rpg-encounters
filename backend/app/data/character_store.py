from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.data.base_store import BaseStore
from app.db.models.character import CharacterORM
from app.models.character import Character, CharacterCreate, CharacterUpdate


class CharacterStore(BaseStore):
    def __init__(
        self,
        user_id: int,
        world_id: int,
        session: AsyncSession = None,
    ):
        super().__init__(user_id=user_id, world_id=world_id, session=session)

    async def get_all_characters(self) -> List[Character]:
        """Get all characters for the current user and world"""
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

    async def get_character_by_id(self, character_id: int) -> Character | None:
        """Get a specific character by ID for the current user and world"""
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

    async def create_character(self, character_data: CharacterCreate) -> Character:
        """Create a new character"""
        async with self.get_session() as session:
            character_orm = CharacterORM(
                **character_data.model_dump(),
                user_id=self.user_id,
                world_id=self.world_id
            )
            session.add(character_orm)
            await session.flush()
            await session.refresh(character_orm)
            return Character.model_validate(character_orm)

    async def update_character(
        self, character_id: int, character_update: CharacterUpdate
    ) -> Character | None:
        """Update an existing character for the current user and world"""
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

    async def delete_character(self, character_id: int) -> bool:
        """Delete a character for the current user and world"""
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

    async def character_exists(self, character_id: int) -> bool:
        """Check if a character exists for the current user and world"""
        async with self.get_session() as session:
            result = await session.execute(
                select(CharacterORM).where(
                    CharacterORM.id == character_id,
                    CharacterORM.user_id == self.user_id,
                    CharacterORM.world_id == self.world_id,
                )
            )
            return result.scalars().first() is not None
