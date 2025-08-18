from typing import List

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.connection import REVEALS_TABLE
from app.db.limits import REVEAL_CONTENT_LIMIT, REVEAL_TITLE_LIMIT
from app.db.models.associations import reveal_characters
from app.db.models.base import UnifiedBase
from app.models.reveal import REVEAL_DEFAULT_THRESHOLDS, RevealLayer


class RevealORM(UnifiedBase):
    __tablename__ = REVEALS_TABLE

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(REVEAL_TITLE_LIMIT))
    level_1_content: Mapped[str] = mapped_column(String(REVEAL_CONTENT_LIMIT))
    level_2_content: Mapped[str | None] = mapped_column(
        String(REVEAL_CONTENT_LIMIT), nullable=True
    )
    level_3_content: Mapped[str | None] = mapped_column(
        String(REVEAL_CONTENT_LIMIT), nullable=True
    )
    standard_threshold: Mapped[int] = mapped_column(
        Integer, default=REVEAL_DEFAULT_THRESHOLDS[RevealLayer.STANDARD]
    )
    privileged_threshold: Mapped[int] = mapped_column(
        Integer, default=REVEAL_DEFAULT_THRESHOLDS[RevealLayer.PRIVILEGED]
    )
    exclusive_threshold: Mapped[int] = mapped_column(
        Integer, default=REVEAL_DEFAULT_THRESHOLDS[RevealLayer.EXCLUSIVE]
    )

    # Direct many-to-many relationship
    characters: Mapped[List["CharacterORM"]] = relationship(  # noqa: F821
        secondary=reveal_characters, back_populates="reveals"
    )
