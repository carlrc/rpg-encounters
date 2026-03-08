import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.db.connection import PLAYERS_TABLE, USERS_TABLE, WORLDS_TABLE
from app.db.models.base import SimpleBase

PLAYER_MAGIC_LINKS_TABLE = "player_magic_links"


class PlayerMagicLinkORM(SimpleBase):
    __tablename__ = PLAYER_MAGIC_LINKS_TABLE

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    player_id: Mapped[int] = mapped_column(
        ForeignKey(f"{PLAYERS_TABLE}.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey(f"{USERS_TABLE}.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    world_id: Mapped[int] = mapped_column(
        ForeignKey(f"{WORLDS_TABLE}.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    token_hash: Mapped[str] = mapped_column(
        String(128), unique=True, nullable=False, index=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    used: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    used_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
