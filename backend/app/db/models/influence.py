from sqlalchemy import ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.connection import INFLUENCES_TABLE
from app.db.models.base import UnifiedBase


class InfluenceORM(UnifiedBase):
    __tablename__ = INFLUENCES_TABLE

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    character_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("characters.id", ondelete="CASCADE"), nullable=False
    )
    player_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("players.id", ondelete="CASCADE"), nullable=False
    )
    base: Mapped[int] = mapped_column(Integer, default=0)
    earned: Mapped[int] = mapped_column(Integer, default=0)

    # Ensure unique character-player pairs
    __table_args__ = (
        UniqueConstraint("character_id", "player_id", name="_character_player_uc"),
    )
