import logging
from typing import List

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.data.base_store import BaseStore
from app.db.models.character import CharacterORM
from app.db.models.reveal import RevealORM
from app.models.reveal import Reveal, RevealCreate, RevealUpdate

logger = logging.getLogger(__name__)


class RevealStore(BaseStore):
    def __init__(
        self,
        user_id: int,
        world_id: int,
        session: AsyncSession | None = None,
    ):
        super().__init__(user_id=user_id, world_id=world_id, session=session)

    async def get_all(self) -> List[Reveal]:
        """Get all reveals for the current user and world"""
        try:
            async with self.get_session() as session:
                result = await session.execute(
                    select(RevealORM)
                    .options(selectinload(RevealORM.characters))
                    .where(
                        RevealORM.user_id == self.user_id,
                        RevealORM.world_id == self.world_id,
                    )
                )
                reveal_orms = result.scalars().all()
                return [
                    RevealStore.orm_to_reveal(reveal_orm) for reveal_orm in reveal_orms
                ]
        except SQLAlchemyError as e:
            logger.error(
                f"Error in get_all for user {self.user_id}, world {self.world_id}: {e}"
            )
            raise

    async def get_by_character_id(self, character_id: int) -> List[Reveal]:
        """Get all reveals for a character"""
        try:
            async with self.get_session() as session:
                result = await session.execute(
                    select(CharacterORM)
                    .options(
                        selectinload(CharacterORM.reveals).selectinload(
                            RevealORM.characters
                        )
                    )
                    .where(CharacterORM.id == character_id)
                )
                character = result.scalars().first()

                if character:
                    return [
                        RevealStore.orm_to_reveal(reveal)
                        for reveal in character.reveals
                    ]
                else:
                    return []
        except SQLAlchemyError as e:
            logger.error(
                f"Error in get_by_character_id for user {self.user_id}, world {self.world_id}, character {character_id}: {e}"
            )
            raise

    async def get_by_id(self, reveal_id: int) -> Reveal | None:
        """Get a specific reveal by ID for the current user and world"""
        try:
            async with self.get_session() as session:
                result = await session.execute(
                    select(RevealORM)
                    .options(selectinload(RevealORM.characters))
                    .where(
                        RevealORM.id == reveal_id,
                        RevealORM.user_id == self.user_id,
                        RevealORM.world_id == self.world_id,
                    )
                )
                reveal_orm = result.scalars().first()
                if reveal_orm:
                    return RevealStore.orm_to_reveal(reveal_orm)
                return None
        except SQLAlchemyError as e:
            logger.error(
                f"Error in get_by_id for user {self.user_id}, world {self.world_id}, reveal {reveal_id}: {e}"
            )
            raise

    async def create(self, reveal_data: RevealCreate) -> Reveal:
        """Create a new reveal"""
        try:
            async with self.get_session() as session:
                # Create the reveal without character_ids - much cleaner!
                reveal_dict = reveal_data.model_dump(exclude={"character_ids"})
                reveal_orm = RevealORM(
                    **reveal_dict, user_id=self.user_id, world_id=self.world_id
                )

                # Automatic association handling - always set characters to avoid lazy loading
                if reveal_data.character_ids:
                    result = await session.execute(
                        select(CharacterORM).where(
                            CharacterORM.id.in_(reveal_data.character_ids)
                        )
                    )
                    characters = result.scalars().all()
                    reveal_orm.characters = characters
                else:
                    reveal_orm.characters = []  # Set empty list to avoid lazy loading

                session.add(reveal_orm)
                await session.flush()
                return RevealStore.orm_to_reveal(reveal_orm)
        except SQLAlchemyError as e:
            logger.error(
                f"Error in create for user {self.user_id}, world {self.world_id}: {e}"
            )
            raise

    async def update(
        self, reveal_id: int, reveal_update: RevealUpdate
    ) -> Reveal | None:
        """Update an existing reveal"""
        try:
            async with self.get_session() as session:
                result = await session.execute(
                    select(RevealORM)
                    .options(selectinload(RevealORM.characters))
                    .where(
                        RevealORM.id == reveal_id,
                        RevealORM.user_id == self.user_id,
                        RevealORM.world_id == self.world_id,
                    )
                )
                reveal_orm = result.scalars().first()

                if not reveal_orm:
                    return None

                # Update basic fields
                update_data = reveal_update.model_dump(
                    exclude={"character_ids"}, exclude_unset=True
                )
                for key, value in update_data.items():
                    setattr(reveal_orm, key, value)

                # Update character relationships
                if reveal_update.character_ids is not None:
                    result = await session.execute(
                        select(CharacterORM).where(
                            CharacterORM.id.in_(reveal_update.character_ids)
                        )
                    )
                    characters = result.scalars().all()
                    reveal_orm.characters = characters

                await session.flush()
                await session.refresh(reveal_orm)
                return RevealStore.orm_to_reveal(reveal_orm)
        except SQLAlchemyError as e:
            logger.error(
                f"Error in update for user {self.user_id}, world {self.world_id}, reveal {reveal_id}: {e}"
            )
            raise

    async def delete(self, reveal_id: int) -> bool:
        """Delete a reveal"""
        try:
            async with self.get_session() as session:
                result = await session.execute(
                    select(RevealORM).where(
                        RevealORM.id == reveal_id,
                        RevealORM.user_id == self.user_id,
                        RevealORM.world_id == self.world_id,
                    )
                )
                reveal_orm = result.scalars().first()
                if not reveal_orm:
                    return False

                await session.delete(reveal_orm)
                return True
        except SQLAlchemyError as e:
            logger.error(
                f"Error in delete for user {self.user_id}, world {self.world_id}, reveal {reveal_id}: {e}"
            )
            raise

    async def exists(self, reveal_id: int) -> bool:
        """Check if a reveal exists"""
        try:
            async with self.get_session() as session:
                result = await session.execute(
                    select(RevealORM).where(
                        RevealORM.id == reveal_id,
                        RevealORM.user_id == self.user_id,
                        RevealORM.world_id == self.world_id,
                    )
                )
                return result.scalars().first() is not None
        except SQLAlchemyError as e:
            logger.error(
                f"Error in exists for user {self.user_id}, world {self.world_id}, reveal {reveal_id}: {e}"
            )
            raise

    @staticmethod
    def orm_to_reveal(reveal_orm: RevealORM) -> Reveal:
        """Convert RevealORM to Reveal model"""
        return Reveal(
            id=reveal_orm.id,
            user_id=reveal_orm.user_id,
            world_id=reveal_orm.world_id,
            title=reveal_orm.title,
            character_ids=[char.id for char in reveal_orm.characters],
            level_1_content=reveal_orm.level_1_content,
            level_2_content=reveal_orm.level_2_content,
            level_3_content=reveal_orm.level_3_content,
            standard_threshold=reveal_orm.standard_threshold,
            privileged_threshold=reveal_orm.privileged_threshold,
            exclusive_threshold=reveal_orm.exclusive_threshold,
        )
