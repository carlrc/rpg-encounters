from typing import List

from sqlalchemy import JSON, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.connection import CHARACTERS_TABLE
from app.db.limits import (
    CHARACTER_BACKGROUND_LIMIT,
    CHARACTER_COMMUNICATION_LIMIT,
    CHARACTER_MOTIVATION_LIMIT,
    NAME_LIMIT,
)
from app.db.models.associations import (
    encounter_characters,
    memory_characters,
    reveal_characters,
)
from app.db.models.base import UnifiedBase
from app.models.character import CommunicationStyle


class CharacterORM(UnifiedBase):
    __tablename__ = CHARACTERS_TABLE

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(NAME_LIMIT))
    race: Mapped[str] = mapped_column(String(50))
    size: Mapped[str] = mapped_column(String(20))
    alignment: Mapped[str] = mapped_column(String(50))
    gender: Mapped[str] = mapped_column(String(20))
    profession: Mapped[str] = mapped_column(String(100))
    background: Mapped[str] = mapped_column(String(CHARACTER_BACKGROUND_LIMIT))
    communication_style: Mapped[str] = mapped_column(
        String(CHARACTER_COMMUNICATION_LIMIT)
    )
    communication_style_examples: Mapped[List[str] | None] = mapped_column(
        JSON, nullable=True
    )
    communication_style_type: Mapped[str] = mapped_column(
        String(20), default=CommunicationStyle.CUSTOM.value
    )
    motivation: Mapped[str] = mapped_column(String(CHARACTER_MOTIVATION_LIMIT))
    personality: Mapped[str] = mapped_column(Text, default="")
    voice_id: Mapped[str] = mapped_column(String(100))
    voice_name: Mapped[str] = mapped_column(String(200))
    tts_provider: Mapped[str] = mapped_column(String(50))

    # Bias preferences stored as JSON
    race_preferences: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    class_preferences: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    gender_preferences: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    size_preferences: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    # Direct many-to-many relationships
    memories: Mapped[List["MemoryORM"]] = relationship(  # noqa: F821
        secondary=memory_characters, back_populates="characters"
    )

    encounters: Mapped[List["EncounterORM"]] = relationship(  # noqa: F821
        secondary=encounter_characters, back_populates="characters"
    )

    reveals: Mapped[List["RevealORM"]] = relationship(  # noqa: F821
        secondary=reveal_characters, back_populates="characters"
    )

    influences: Mapped[List["InfluenceORM"]] = relationship(  # noqa: F821
        foreign_keys="InfluenceORM.character_id"
    )
