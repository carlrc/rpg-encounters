from typing import List

from sqlalchemy.orm import sessionmaker

from app.db.connection import get_db_engine
from app.db.models.character import CharacterORM
from app.db.models.memory import MemoryORM
from app.models.memory import Memory, MemoryCreate, MemoryUpdate


class MemoryStore:
    def __init__(self):
        self.Session = sessionmaker(get_db_engine())

    def get_all_memories(self) -> List[Memory]:
        """Get all memories across all characters"""
        with self.Session() as session:
            memory_orms = session.query(MemoryORM).all()
            return [self._orm_to_memory(memory_orm) for memory_orm in memory_orms]

    def get_by_character_id(self, character_id: int) -> List[Memory]:
        """Get all memories for a character"""
        with self.Session() as session:
            memory_orms = (
                session.query(MemoryORM)
                .join(MemoryORM.characters)
                .filter(CharacterORM.id == character_id)
                .all()
            )
            return [self._orm_to_memory(memory_orm) for memory_orm in memory_orms]

    def get_memory(self, memory_id: int) -> Memory | None:
        """Get a specific memory by ID"""
        with self.Session() as session:
            memory_orm = (
                session.query(MemoryORM).filter(MemoryORM.id == memory_id).first()
            )
            if memory_orm:
                return self._orm_to_memory(memory_orm)
            return None

    def get_by_id(self, memory_id: int) -> Memory | None:
        """Get a specific memory by ID (alias for get_memory)"""
        return self.get_memory(memory_id)

    def create_memory(self, memory_data: MemoryCreate) -> Memory:
        """Create a new memory"""
        with self.Session() as session:
            # Create the memory without character_ids
            memory_dict = memory_data.model_dump(exclude={"character_ids"})
            memory_orm = MemoryORM(**memory_dict)
            session.add(memory_orm)
            session.flush()  # Get the ID without committing

            # Add character associations
            if memory_data.character_ids:
                characters = (
                    session.query(CharacterORM)
                    .filter(CharacterORM.id.in_(memory_data.character_ids))
                    .all()
                )
                memory_orm.characters = characters

            session.commit()
            session.refresh(memory_orm)
            return self._orm_to_memory(memory_orm)

    def update_memory(
        self, memory_id: int, memory_update: MemoryUpdate
    ) -> Memory | None:
        """Update an existing memory"""
        with self.Session() as session:
            memory_orm = (
                session.query(MemoryORM).filter(MemoryORM.id == memory_id).first()
            )
            if not memory_orm:
                return None

            # Update basic fields
            update_data = memory_update.model_dump(
                exclude={"character_ids"}, exclude_unset=True
            )
            for key, value in update_data.items():
                setattr(memory_orm, key, value)

            # Update character associations if provided
            if (
                hasattr(memory_update, "character_ids")
                and memory_update.character_ids is not None
            ):
                characters = (
                    session.query(CharacterORM)
                    .filter(CharacterORM.id.in_(memory_update.character_ids))
                    .all()
                )
                memory_orm.characters = characters

            session.commit()
            session.refresh(memory_orm)
            return self._orm_to_memory(memory_orm)

    def delete_memory(self, memory_id: int) -> bool:
        """Delete a memory"""
        with self.Session() as session:
            memory_orm = (
                session.query(MemoryORM).filter(MemoryORM.id == memory_id).first()
            )
            if not memory_orm:
                return False

            session.delete(memory_orm)
            session.commit()
            return True

    def memory_exists(self, memory_id: int) -> bool:
        """Check if a memory exists"""
        with self.Session() as session:
            return (
                session.query(MemoryORM).filter(MemoryORM.id == memory_id).first()
                is not None
            )

    def _orm_to_memory(self, memory_orm: MemoryORM) -> Memory:
        """Convert MemoryORM to Memory model"""
        return Memory(
            id=memory_orm.id,
            title=memory_orm.title,
            content=memory_orm.content,
            character_ids=[char.id for char in memory_orm.characters],
        )
