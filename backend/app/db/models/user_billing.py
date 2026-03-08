from datetime import datetime, timezone

from sqlalchemy import BigInteger, DateTime, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column

from app.db.connection import USER_BILLING_TABLE, USERS_TABLE
from app.db.models.base import SimpleBase


class UserBillingORM(SimpleBase):
    __tablename__ = USER_BILLING_TABLE

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey(f"{USERS_TABLE}.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    available_tokens: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
    last_used_tokens: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
    total_used_tokens: Mapped[int] = mapped_column(
        BigInteger, nullable=False, default=0
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
