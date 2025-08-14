from typing import List

from sqlalchemy import Column, ForeignKey, Integer, String, Table
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from app.db.connection import MEMORIES_TABLE
from app.db.limits import CONTENT_LIMIT

# Import for forward reference
from app.db.models.character import CharacterORM


class Base(DeclarativeBase):
    pass


# Association table for many-to-many relationship between memories and characters
memory_character_association = Table(
    "memory_characters",
    Base.metadata,
    Column("memory_id", Integer, ForeignKey("memories.id"), primary_key=True),
    Column("character_id", Integer, ForeignKey("characters.id"), primary_key=True),
)


class MemoryORM(Base):
    __tablename__ = MEMORIES_TABLE

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255))
    content: Mapped[str] = mapped_column(String(CONTENT_LIMIT))

    # Many-to-many relationship with characters
    characters: Mapped[List[CharacterORM]] = relationship(
        "CharacterORM",
        secondary=memory_character_association,
        back_populates="memories",
    )
