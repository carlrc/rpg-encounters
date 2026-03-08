from sqlalchemy import ForeignKey, Integer, LargeBinary
from sqlalchemy.orm import Mapped, mapped_column

from app.db.connection import (
    CHARACTERS_TABLE,
    CONVERSATIONS_TABLE,
    ENCOUNTERS_TABLE,
    PLAYERS_TABLE,
)
from app.db.models.base import UnifiedBase


class ConversationORM(UnifiedBase):
    __tablename__ = CONVERSATIONS_TABLE

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    player_id: Mapped[int] = mapped_column(
        Integer, ForeignKey(f"{PLAYERS_TABLE}.id", ondelete="CASCADE")
    )
    character_id: Mapped[int] = mapped_column(
        Integer, ForeignKey(f"{CHARACTERS_TABLE}.id", ondelete="CASCADE")
    )
    encounter_id: Mapped[int] = mapped_column(
        Integer, ForeignKey(f"{ENCOUNTERS_TABLE}.id", ondelete="CASCADE")
    )
    messages: Mapped[bytes | None] = mapped_column(LargeBinary, nullable=True)
