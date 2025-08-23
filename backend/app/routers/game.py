from fastapi import APIRouter

from app.db.limits import (
    CHARACTER_BACKGROUND_LIMIT,
    CHARACTER_COMMUNICATION_LIMIT,
    CHARACTER_MOTIVATION_LIMIT,
    CHARACTER_PROFESSION_LIMIT,
    MEMORY_CONTENT_LIMIT,
    NAME_LIMIT,
    PLAYER_APPEARANCE_MAX_LIMIT,
    REVEAL_CONTENT_LIMIT,
    TITLE_LIMIT,
)
from app.models.alignment import VALID_ALIGNMENTS
from app.models.class_traits import VALID_CLASSES, VALID_SKILLS
from app.models.race import VALID_RACES, VALID_SIZES
from app.models.reveal import REVEAL_DEFAULT_THRESHOLDS, DifficultyClass, RevealLayer

router = APIRouter(prefix="/api/game", tags=["games"])


@router.get("/")
async def get_game_data():
    """Get all game data constants for frontend caching"""
    return {
        "races": VALID_RACES,
        "classes": VALID_CLASSES,
        "alignments": VALID_ALIGNMENTS,
        "skills": VALID_SKILLS,
        "sizes": {
            "player": VALID_SIZES,
            "character": VALID_SIZES + ["Large"],
        },
        "difficulty_classes": {dc.name: dc.value for dc in DifficultyClass},
        "default_thresholds": {
            "standard": REVEAL_DEFAULT_THRESHOLDS[RevealLayer.STANDARD],
            "privileged": REVEAL_DEFAULT_THRESHOLDS[RevealLayer.PRIVILEGED],
            "exclusive": REVEAL_DEFAULT_THRESHOLDS[RevealLayer.EXCLUSIVE],
        },
        "validation_limits": {
            # All limits are character-based
            "name": NAME_LIMIT,
            "player_appearance": PLAYER_APPEARANCE_MAX_LIMIT,
            "character_profession": CHARACTER_PROFESSION_LIMIT,
            "character_background": CHARACTER_BACKGROUND_LIMIT,
            "character_communication": CHARACTER_COMMUNICATION_LIMIT,
            "character_motivation": CHARACTER_MOTIVATION_LIMIT,
            "memory_title": TITLE_LIMIT,
            "memory_content": MEMORY_CONTENT_LIMIT,
            "reveal_title": TITLE_LIMIT,
            "reveal_content": REVEAL_CONTENT_LIMIT,
        },
        "threshold_limits": {
            "min": DifficultyClass.ALWAYS.value,
            "max": DifficultyClass.NEARLY_IMPOSSIBLE.value,
            "step": 5,
            "min_gap": 5,
        },
    }
