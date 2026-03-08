from typing import List

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.connection import MEMORIES_TABLE
from app.db.limits import MEMORY_CONTENT_LIMIT, TITLE_LIMIT
from app.db.models.associations import memory_characters
from app.db.models.base import UnifiedBase


class MemoryORM(UnifiedBase):
    __tablename__ = MEMORIES_TABLE

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(TITLE_LIMIT))
    content: Mapped[str] = mapped_column(String(MEMORY_CONTENT_LIMIT))

    # Direct many-to-many relationship
    characters: Mapped[List["CharacterORM"]] = relationship(  # noqa: F821
        secondary=memory_characters, back_populates="memories"
    )
