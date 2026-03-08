from sqlalchemy import Column, ForeignKey, Table

from app.db.connection import (
    CHARACTERS_TABLE,
    ENCOUNTERS_TABLE,
    MEMORIES_TABLE,
    PLAYERS_TABLE,
    REVEALS_TABLE,
)
from app.db.models.base import SimpleBase

# Association tables - NOT ORM models
memory_characters = Table(
    "memory_characters",
    SimpleBase.metadata,
    Column(
        "memory_id",
        ForeignKey(f"{MEMORIES_TABLE}.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "character_id",
        ForeignKey(f"{CHARACTERS_TABLE}.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)

encounter_characters = Table(
    "encounter_characters",
    SimpleBase.metadata,
    Column(
        "encounter_id",
        ForeignKey(f"{ENCOUNTERS_TABLE}.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "character_id",
        ForeignKey(f"{CHARACTERS_TABLE}.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)

encounter_players = Table(
    "encounter_players",
    SimpleBase.metadata,
    Column(
        "encounter_id",
        ForeignKey(f"{ENCOUNTERS_TABLE}.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "player_id",
        ForeignKey(f"{PLAYERS_TABLE}.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)

reveal_characters = Table(
    "reveal_characters",
    SimpleBase.metadata,
    Column(
        "reveal_id",
        ForeignKey(f"{REVEALS_TABLE}.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "character_id",
        ForeignKey(f"{CHARACTERS_TABLE}.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)
