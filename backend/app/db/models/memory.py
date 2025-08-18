from typing import List

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.connection import MEMORIES_TABLE
from app.db.limits import MEMORY_CONTENT_LIMIT
from app.db.models.associations import memory_characters
from app.db.models.base import UnifiedBase


class MemoryORM(UnifiedBase):
    __tablename__ = MEMORIES_TABLE

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255))
    content: Mapped[str] = mapped_column(String(MEMORY_CONTENT_LIMIT))

    # Direct many-to-many relationship
    characters: Mapped[List["CharacterORM"]] = relationship(  # noqa: F821
        secondary=memory_characters, back_populates="memories"
    )
