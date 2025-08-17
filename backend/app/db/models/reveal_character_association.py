from sqlalchemy import Column, ForeignKey, Integer, Table

from app.db.models.base import UnifiedBase

# Association table for many-to-many relationship between reveals and characters
reveal_character_association = Table(
    "reveal_characters",
    UnifiedBase.metadata,
    Column("reveal_id", Integer, ForeignKey("reveals.id"), primary_key=True),
    Column("character_id", Integer, ForeignKey("characters.id"), primary_key=True),
)
