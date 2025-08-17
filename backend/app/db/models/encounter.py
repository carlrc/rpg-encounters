from sqlalchemy import Float, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.connection import ENCOUNTERS_TABLE
from app.db.limits import ENCOUNTER_DESCRIPTION_LIMIT, ENCOUNTER_NAME_LIMIT
from app.db.models.base import UnifiedBase
from app.db.models.encounter_character_association import (
    encounter_character_association,
)


class EncounterORM(UnifiedBase):
    __tablename__ = ENCOUNTERS_TABLE

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(ENCOUNTER_NAME_LIMIT))
    description: Mapped[str | None] = mapped_column(
        String(ENCOUNTER_DESCRIPTION_LIMIT), nullable=True
    )
    position_x: Mapped[float] = mapped_column(Float)
    position_y: Mapped[float] = mapped_column(Float)

    # Many-to-many relationship with characters
    characters = relationship(
        "CharacterORM",
        secondary=encounter_character_association,
        back_populates="encounters",
    )

    # One-to-many relationships with connections
    outgoing_connections = relationship(
        "ConnectionORM",
        foreign_keys="ConnectionORM.source_encounter_id",
        back_populates="source_encounter",
        cascade="all, delete-orphan",
    )
    incoming_connections = relationship(
        "ConnectionORM",
        foreign_keys="ConnectionORM.target_encounter_id",
        back_populates="target_encounter",
        cascade="all, delete-orphan",
    )
