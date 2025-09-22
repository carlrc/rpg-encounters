from typing import List

from sqlalchemy import JSON, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.connection import PLAYERS_TABLE
from app.db.limits import NAME_LIMIT, PLAYER_APPEARANCE_MAX_LIMIT
from app.db.models.associations import encounter_players
from app.db.models.base import UnifiedBase


class PlayerORM(UnifiedBase):
    __tablename__ = PLAYERS_TABLE

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(NAME_LIMIT), nullable=False)
    rl_name: Mapped[str] = mapped_column(String(NAME_LIMIT), nullable=False)
    appearance: Mapped[str] = mapped_column(
        String(PLAYER_APPEARANCE_MAX_LIMIT), nullable=False
    )
    race: Mapped[str] = mapped_column(String(50), nullable=False)
    class_name: Mapped[str] = mapped_column(String(50), nullable=False)
    size: Mapped[str] = mapped_column(String(20), nullable=False)
    alignment: Mapped[str] = mapped_column(String(50), nullable=False)
    gender: Mapped[str] = mapped_column(String(20), nullable=False)
    abilities: Mapped[dict] = mapped_column(JSON, nullable=False)
    skills: Mapped[dict] = mapped_column(JSON, nullable=False)

    # Many-to-many relationship with encounters
    encounters: Mapped[List["EncounterORM"]] = relationship(  # noqa: F821
        secondary=encounter_players, back_populates="players"
    )

    # One-to-many relationship with influences
    influences = relationship("InfluenceORM", foreign_keys="InfluenceORM.player_id")
