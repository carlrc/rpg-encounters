from typing import List

from sqlalchemy import Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.connection import ENCOUNTERS_TABLE
from app.db.limits import ENCOUNTER_DESCRIPTION_LIMIT, TITLE_LIMIT
from app.db.models.associations import encounter_characters
from app.db.models.base import UnifiedBase

# Import all ORM models to ensure they are registered with SQLAlchemy
from app.db.models.user import UserORM  # noqa: F401
from app.db.models.world import WorldORM  # noqa: F401


class EncounterORM(UnifiedBase):
    __tablename__ = ENCOUNTERS_TABLE

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(TITLE_LIMIT))
    description: Mapped[str | None] = mapped_column(
        String(ENCOUNTER_DESCRIPTION_LIMIT), nullable=True
    )
    position_x: Mapped[float] = mapped_column(Float)
    position_y: Mapped[float] = mapped_column(Float)

    # Direct many-to-many relationship
    characters: Mapped[List["CharacterORM"]] = relationship(  # noqa: F821
        secondary=encounter_characters, back_populates="encounters"
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
