from sqlalchemy import JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.connection import CHARACTERS_TABLE
from app.db.limits import (
    CHARACTER_BACKGROUND_LIMIT,
    CHARACTER_COMMUNICATION_LIMIT,
    CHARACTER_MOTIVATION_LIMIT,
)
from app.db.models.base import CharacterMemoryBase
from app.db.models.memory_character_association import memory_character_association


class CharacterORM(CharacterMemoryBase):
    __tablename__ = CHARACTERS_TABLE

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    avatar: Mapped[str | None] = mapped_column(Text, nullable=True)
    race: Mapped[str] = mapped_column(String(50))
    size: Mapped[str] = mapped_column(String(20))
    alignment: Mapped[str] = mapped_column(String(50))
    gender: Mapped[str] = mapped_column(String(20))
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

    memories = relationship(
        "MemoryORM",
        secondary=memory_character_association,
        back_populates="characters",
    )
