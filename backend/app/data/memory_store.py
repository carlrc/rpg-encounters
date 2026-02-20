import logging
from typing import List

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.data.base_store import BaseStore
from app.db.models.character import CharacterORM
from app.db.models.memory import MemoryORM
from app.models.memory import Memory, MemoryCreate, MemoryUpdate

logger = logging.getLogger(__name__)


class MemoryStore(BaseStore):
    def __init__(
        self,
        user_id: int,
        world_id: int,
        session: AsyncSession | None = None,
    ):
        super().__init__(user_id=user_id, world_id=world_id, session=session)

    async def get_all(self) -> List[Memory]:
        """Get all memories for the current user and world"""
        try:
            async with self.get_session() as session:
                result = await session.execute(
                    select(MemoryORM)
                    .options(selectinload(MemoryORM.characters))
                    .where(
                        MemoryORM.user_id == self.user_id,
                        MemoryORM.world_id == self.world_id,
                    )
                )
                memory_orms = result.scalars().all()
                return [
                    MemoryStore.orm_to_memory(memory_orm) for memory_orm in memory_orms
                ]
        except SQLAlchemyError as e:
            logger.error(
                f"Error in get_all for user {self.user_id}, world {self.world_id}: {e}"
            )
            raise

    async def get_by_character_id(self, character_id: int) -> List[Memory]:
        """Get all memories for a character using relationship"""
        try:
            async with self.get_session() as session:
                result = await session.execute(
                    select(CharacterORM)
                    .options(
                        selectinload(CharacterORM.memories).selectinload(
                            MemoryORM.characters
                        )
                    )
                    .where(CharacterORM.id == character_id)
                )
                character = result.scalars().first()

                if character:
                    return [
                        MemoryStore.orm_to_memory(memory)
                        for memory in character.memories
                    ]
                else:
                    return []
        except SQLAlchemyError as e:
            logger.error(
                f"Error in get_by_character_id for user {self.user_id}, world {self.world_id}, character {character_id}: {e}"
            )
            raise

    async def get_by_id(self, memory_id: int) -> Memory | None:
        """Get a specific memory by ID for the current user and world"""
        try:
            async with self.get_session() as session:
                result = await session.execute(
                    select(MemoryORM)
                    .options(selectinload(MemoryORM.characters))
                    .where(
                        MemoryORM.id == memory_id,
                        MemoryORM.user_id == self.user_id,
                        MemoryORM.world_id == self.world_id,
                    )
                )
                memory_orm = result.scalars().first()
                if memory_orm:
                    return MemoryStore.orm_to_memory(memory_orm)
                return None
        except SQLAlchemyError as e:
            logger.error(
                f"Error in get_by_id for user {self.user_id}, world {self.world_id}, memory {memory_id}: {e}"
            )
            raise

    async def create(self, memory_data: MemoryCreate) -> Memory:
        """Create a new memory with automatic association management"""
        try:
            async with self.get_session() as session:
                memory_orm = MemoryORM(
                    title=memory_data.title,
                    content=memory_data.content,
                    user_id=self.user_id,
                    world_id=self.world_id,
                )

                # SQLAlchemy handles associations automatically - always set characters to avoid lazy loading
                if memory_data.character_ids:
                    result = await session.execute(
                        select(CharacterORM).where(
                            CharacterORM.id.in_(memory_data.character_ids)
                        )
                    )
                    characters = result.scalars().all()
                    memory_orm.characters = characters
                else:
                    memory_orm.characters = []  # Set empty list to avoid lazy loading

                session.add(memory_orm)
                await session.flush()
                # No need to refresh since we already have the relationships loaded
                return MemoryStore.orm_to_memory(memory_orm)
        except SQLAlchemyError as e:
            logger.error(
                f"Error in create for user {self.user_id}, world {self.world_id}: {e}"
            )
            raise

    async def update(
        self, memory_id: int, memory_update: MemoryUpdate
    ) -> Memory | None:
        """Update memory with simplified association handling"""
        try:
            async with self.get_session() as session:
                result = await session.execute(
                    select(MemoryORM)
                    .options(selectinload(MemoryORM.characters))
                    .where(
                        MemoryORM.id == memory_id,
                        MemoryORM.user_id == self.user_id,
                        MemoryORM.world_id == self.world_id,
                    )
                )
                memory_orm = result.scalars().first()

                if not memory_orm:
                    return None

                # Update basic fields
                update_data = memory_update.model_dump(
                    exclude={"character_ids"}, exclude_unset=True
                )
                for key, value in update_data.items():
                    setattr(memory_orm, key, value)

                # Update character relationships - SQLAlchemy handles everything!
                if memory_update.character_ids is not None:
                    result = await session.execute(
                        select(CharacterORM).where(
                            CharacterORM.id.in_(memory_update.character_ids)
                        )
                    )
                    characters = result.scalars().all()
                    memory_orm.characters = characters

                await session.flush()
                await session.refresh(memory_orm)
                return MemoryStore.orm_to_memory(memory_orm)
        except SQLAlchemyError as e:
            logger.error(
                f"Error in update for user {self.user_id}, world {self.world_id}, memory {memory_id}: {e}"
            )
            raise

    async def delete(self, memory_id: int) -> bool:
        """Delete a memory"""
        try:
            async with self.get_session() as session:
                result = await session.execute(
                    select(MemoryORM).where(
                        MemoryORM.id == memory_id,
                        MemoryORM.user_id == self.user_id,
                        MemoryORM.world_id == self.world_id,
                    )
                )
                memory_orm = result.scalars().first()
                if not memory_orm:
                    return False

                await session.delete(memory_orm)  # Cascade handles associations
                return True
        except SQLAlchemyError as e:
            logger.error(
                f"Error in delete for user {self.user_id}, world {self.world_id}, memory {memory_id}: {e}"
            )
            raise

    async def exists(self, memory_id: int) -> bool:
        """Check if a memory exists"""
        try:
            async with self.get_session() as session:
                result = await session.execute(
                    select(MemoryORM).where(
                        MemoryORM.id == memory_id,
                        MemoryORM.user_id == self.user_id,
                        MemoryORM.world_id == self.world_id,
                    )
                )
                return result.scalars().first() is not None
        except SQLAlchemyError as e:
            logger.error(
                f"Error in exists for user {self.user_id}, world {self.world_id}, memory {memory_id}: {e}"
            )
            raise

    @staticmethod
    def orm_to_memory(memory_orm: MemoryORM) -> Memory:
        """Convert MemoryORM to Memory model"""
        return Memory(
            id=memory_orm.id,
            user_id=memory_orm.user_id,
            world_id=memory_orm.world_id,
            title=memory_orm.title,
            content=memory_orm.content,
            character_ids=[char.id for char in memory_orm.characters],
        )
