from typing import List

from sqlalchemy import Engine

from app.data.base_store import BaseStore
from app.db.connection import get_db_engine
from app.db.models.character import CharacterORM
from app.db.models.memory import MemoryORM
from app.models.memory import Memory, MemoryCreate, MemoryUpdate


class MemoryStore(BaseStore):
    def __init__(
        self,
        user_id: int,
        world_id: int,
        engine: Engine = get_db_engine(),
        session=None,
    ):
        super().__init__(
            user_id=user_id, world_id=world_id, engine=engine, session=session
        )

    def get_all_memories(self) -> List[Memory]:
        """Get all memories for the current user and world"""
        with self.get_session() as session:
            memory_orms = (
                session.query(MemoryORM)
                .filter(
                    MemoryORM.user_id == self.user_id,
                    MemoryORM.world_id == self.world_id,
                )
                .all()
            )
            return [MemoryStore.orm_to_memory(memory_orm) for memory_orm in memory_orms]

    def get_by_character_id(self, character_id: int) -> List[Memory]:
        """Get all memories for a character using relationship"""
        with self.get_session() as session:
            character = (
                session.query(CharacterORM)
                .filter(CharacterORM.id == character_id)
                .first()
            )

            if character:
                return [
                    MemoryStore.orm_to_memory(memory) for memory in character.memories
                ]
            else:
                return []

    def get_memory(self, memory_id: int) -> Memory | None:
        """Get a specific memory by ID for the current user and world"""
        with self.get_session() as session:
            memory_orm = (
                session.query(MemoryORM)
                .filter(
                    MemoryORM.id == memory_id,
                    MemoryORM.user_id == self.user_id,
                    MemoryORM.world_id == self.world_id,
                )
                .first()
            )
            if memory_orm:
                return MemoryStore.orm_to_memory(memory_orm)
            return None

    def get_by_id(self, memory_id: int) -> Memory | None:
        """Get a specific memory by ID (alias for get_memory)"""
        return self.get_memory(memory_id)

    def create_memory(self, memory_data: MemoryCreate) -> Memory:
        """Create a new memory with automatic association management"""
        with self.get_session() as session:
            memory_orm = MemoryORM(
                title=memory_data.title,
                content=memory_data.content,
                user_id=self.user_id,
                world_id=self.world_id,
            )

            # SQLAlchemy handles associations automatically
            if memory_data.character_ids:
                characters = (
                    session.query(CharacterORM)
                    .filter(CharacterORM.id.in_(memory_data.character_ids))
                    .all()
                )
                memory_orm.characters = characters

            session.add(memory_orm)
            session.commit()
            session.refresh(memory_orm)
            return MemoryStore.orm_to_memory(memory_orm)

    def update_memory(
        self, memory_id: int, memory_update: MemoryUpdate
    ) -> Memory | None:
        """Update memory with simplified association handling"""
        with self.get_session() as session:
            memory_orm = (
                session.query(MemoryORM)
                .filter(
                    MemoryORM.id == memory_id,
                    MemoryORM.user_id == self.user_id,
                    MemoryORM.world_id == self.world_id,
                )
                .first()
            )

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
                characters = (
                    session.query(CharacterORM)
                    .filter(CharacterORM.id.in_(memory_update.character_ids))
                    .all()
                )
                memory_orm.characters = characters

            session.commit()
            session.refresh(memory_orm)
            return MemoryStore.orm_to_memory(memory_orm)

    def delete_memory(self, memory_id: int) -> bool:
        """Delete a memory"""
        with self.get_session() as session:
            memory_orm = (
                session.query(MemoryORM)
                .filter(
                    MemoryORM.id == memory_id,
                    MemoryORM.user_id == self.user_id,
                    MemoryORM.world_id == self.world_id,
                )
                .first()
            )
            if not memory_orm:
                return False

            session.delete(memory_orm)  # Cascade handles associations
            session.commit()
            return True

    def memory_exists(self, memory_id: int) -> bool:
        """Check if a memory exists"""
        with self.get_session() as session:
            return (
                session.query(MemoryORM)
                .filter(
                    MemoryORM.id == memory_id,
                    MemoryORM.user_id == self.user_id,
                    MemoryORM.world_id == self.world_id,
                )
                .first()
                is not None
            )

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
