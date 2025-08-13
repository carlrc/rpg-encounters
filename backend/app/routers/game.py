from fastapi import APIRouter

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
            "memory_text": 500,
            "player_appearance": 180,
            "character_background": 240,
            "character_communication": 180,
            "character_motivation": 300,
        },
        "threshold_limits": {
            "min": DifficultyClass.ALWAYS.value,
            "max": DifficultyClass.NEARLY_IMPOSSIBLE.value,
            "step": 5,
            "min_gap": 5,
        },
    }
