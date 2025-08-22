from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from app.db.connection import USERS_TABLE, WORLDS_TABLE


class UserWorldBase:
    """Base class to add user_id and world_id as required fields to all models"""

    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey(f"{USERS_TABLE}.id"), nullable=False
    )
    world_id: Mapped[int] = mapped_column(
        Integer, ForeignKey(f"{WORLDS_TABLE}.id", ondelete="CASCADE"), nullable=False
    )


# Simple base for models that don't need user/world fields (like User and World)
class SimpleBase(DeclarativeBase):
    pass


# Unified base for models that need both memory and reveal relationships
class UnifiedBase(SimpleBase, UserWorldBase):
    __abstract__ = True
