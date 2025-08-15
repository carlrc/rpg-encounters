from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.connection import MEMORIES_TABLE
from app.db.limits import CONTENT_LIMIT
from app.db.models.base import UnifiedBase
from app.db.models.memory_character_association import memory_character_association


class MemoryORM(UnifiedBase):
    __tablename__ = MEMORIES_TABLE

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255))
    content: Mapped[str] = mapped_column(String(CONTENT_LIMIT))

    # Many-to-many relationship with characters
    characters = relationship(
        "CharacterORM",
        secondary=memory_character_association,
        back_populates="memories",
    )
