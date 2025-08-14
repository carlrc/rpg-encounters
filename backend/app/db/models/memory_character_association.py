from sqlalchemy import Column, ForeignKey, Integer, Table

from app.db.models.base import CharacterMemoryBase

# Association table for many-to-many relationship between memories and characters
memory_character_association = Table(
    "memory_characters",
    CharacterMemoryBase.metadata,
    Column("memory_id", Integer, ForeignKey("memories.id"), primary_key=True),
    Column("character_id", Integer, ForeignKey("characters.id"), primary_key=True),
)
