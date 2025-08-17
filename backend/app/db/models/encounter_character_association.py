from sqlalchemy import Column, ForeignKey, Integer, Table

from app.db.models.base import UnifiedBase

# Association table for many-to-many relationship between encounters and characters
encounter_character_association = Table(
    "encounter_characters",
    UnifiedBase.metadata,
    Column("encounter_id", Integer, ForeignKey("encounters.id"), primary_key=True),
    Column("character_id", Integer, ForeignKey("characters.id"), primary_key=True),
)
