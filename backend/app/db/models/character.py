from typing import List

from sqlalchemy import JSON, Enum, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from app.db.connection import CHARACTERS_TABLE
from app.db.limits import (
    CHARACTER_BACKGROUND_LIMIT,
    CHARACTER_COMMUNICATION_LIMIT,
    CHARACTER_MOTIVATION_LIMIT,
)
from app.db.models.memory import MemoryORM
from app.models.alignment import Alignment
from app.models.race import Gender, Race, Size


class Base(DeclarativeBase):
    pass


class CharacterORM(Base):
    __tablename__ = CHARACTERS_TABLE

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    avatar: Mapped[str | None] = mapped_column(Text, nullable=True)
    race: Mapped[Race] = mapped_column(Enum(Race))
    size: Mapped[Size] = mapped_column(Enum(Size))
    alignment: Mapped[Alignment] = mapped_column(Enum(Alignment))
    gender: Mapped[Gender] = mapped_column(Enum(Gender))
    profession: Mapped[str] = mapped_column(String(100))
    background: Mapped[str] = mapped_column(String(CHARACTER_BACKGROUND_LIMIT))
    communication_style: Mapped[str] = mapped_column(
        String(CHARACTER_COMMUNICATION_LIMIT)
    )
    motivation: Mapped[str] = mapped_column(String(CHARACTER_MOTIVATION_LIMIT))
    personality: Mapped[str] = mapped_column(Text, default="")
    voice: Mapped[str | None] = mapped_column(
        String(100), nullable=True, default="JBFqnCBsd6RMkjVDRZzb"
    )

    # Bias preferences stored as JSON
    race_preferences: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    class_preferences: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    gender_preferences: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    size_preferences: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    appearance_keywords: Mapped[list | None] = mapped_column(JSON, nullable=True)
    storytelling_keywords: Mapped[list | None] = mapped_column(JSON, nullable=True)

    # Many-to-many relationship with memories
    memories: Mapped[List[MemoryORM]] = relationship(
        "MemoryORM", secondary="memory_characters", back_populates="characters"
    )
