from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.connection import CONNECTIONS_TABLE, ENCOUNTERS_TABLE
from app.db.limits import (
    CONNECTION_COLOR_LIMIT,
    CONNECTION_EDGE_TYPE_LIMIT,
    CONNECTION_HANDLE_LIMIT,
)
from app.db.models.base import UnifiedBase


class ConnectionORM(UnifiedBase):
    __tablename__ = CONNECTIONS_TABLE

    id: Mapped[int] = mapped_column(primary_key=True)
    source_encounter_id: Mapped[int] = mapped_column(
        Integer, ForeignKey(f"{ENCOUNTERS_TABLE}.id", ondelete="CASCADE")
    )
    target_encounter_id: Mapped[int] = mapped_column(
        Integer, ForeignKey(f"{ENCOUNTERS_TABLE}.id", ondelete="CASCADE")
    )
    source_handle: Mapped[str] = mapped_column(
        String(CONNECTION_HANDLE_LIMIT), nullable=False
    )
    target_handle: Mapped[str] = mapped_column(
        String(CONNECTION_HANDLE_LIMIT), nullable=False
    )
    edge_type: Mapped[str] = mapped_column(
        String(CONNECTION_EDGE_TYPE_LIMIT), default="straight"
    )
    stroke_color: Mapped[str] = mapped_column(
        String(CONNECTION_COLOR_LIMIT), default="#007bff"
    )
    stroke_width: Mapped[int] = mapped_column(Integer, default=3)

    # Relationships to encounters
    source_encounter = relationship(
        "EncounterORM",
        foreign_keys=[source_encounter_id],
        back_populates="outgoing_connections",
    )
    target_encounter = relationship(
        "EncounterORM",
        foreign_keys=[target_encounter_id],
        back_populates="incoming_connections",
    )
