from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.connection import MODERATIONS_TABLE, USERS_TABLE
from app.db.models.base import SimpleBase


class ModerationORM(SimpleBase):
    __tablename__ = MODERATIONS_TABLE

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey(f"{USERS_TABLE}.id"), nullable=False
    )
    text: Mapped[str] = mapped_column(Text, nullable=False)
    openai_id: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
