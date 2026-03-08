import logging

from fastapi import APIRouter, Depends

from app.auth.session import PlayerSession, UserSession
from app.clients.tts import get_available_tts_providers
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
from app.dependencies import validate_current_player_or_user
from app.models.alignment import VALID_ALIGNMENTS
from app.models.character import CommunicationStyle
from app.models.class_traits import (
    ABILITY_MODIFIER_MAX,
    ABILITY_MODIFIER_MIN,
    SKILL_MODIFIER_MAX,
    SKILL_MODIFIER_MIN,
    VALID_CLASSES,
    VALID_SKILLS,
)
from app.models.game import (
    DefaultThresholds,
    GameDataResponse,
    ModifierLimits,
    SizeOptions,
    ThresholdLimits,
    ValidationLimits,
)
from app.models.race import VALID_RACES, VALID_SIZES
from app.models.reveal import REVEAL_DEFAULT_THRESHOLDS, DifficultyClass, RevealLayer

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/game", tags=["games"])


@router.get("/", response_model=GameDataResponse)
async def get_game_data(
    session: UserSession | PlayerSession = Depends(validate_current_player_or_user),
) -> GameDataResponse:
    """Get all game data constants for frontend caching"""
    try:
        tts_providers = get_available_tts_providers()
        return GameDataResponse(
            races=VALID_RACES,
            classes=VALID_CLASSES,
            alignments=VALID_ALIGNMENTS,
            skills=VALID_SKILLS,
            communication_styles=[style.value for style in CommunicationStyle],
            sizes=SizeOptions(player=VALID_SIZES, character=VALID_SIZES),
            difficulty_classes={dc.name: dc.value for dc in DifficultyClass},
            default_thresholds=DefaultThresholds(
                standard=REVEAL_DEFAULT_THRESHOLDS[RevealLayer.STANDARD],
                privileged=REVEAL_DEFAULT_THRESHOLDS[RevealLayer.PRIVILEGED],
                exclusive=REVEAL_DEFAULT_THRESHOLDS[RevealLayer.EXCLUSIVE],
            ),
            validation_limits=ValidationLimits(
                name=NAME_LIMIT,
                player_appearance=PLAYER_APPEARANCE_MAX_LIMIT,
                character_profession=CHARACTER_PROFESSION_LIMIT,
                character_background=CHARACTER_BACKGROUND_LIMIT,
                character_communication=CHARACTER_COMMUNICATION_LIMIT,
                character_motivation=CHARACTER_MOTIVATION_LIMIT,
                memory_title=TITLE_LIMIT,
                memory_content=MEMORY_CONTENT_LIMIT,
                reveal_title=TITLE_LIMIT,
                reveal_content=REVEAL_CONTENT_LIMIT,
            ),
            threshold_limits=ThresholdLimits(
                min=DifficultyClass.ALWAYS.value,
                max=DifficultyClass.NEARLY_IMPOSSIBLE.value,
                step=5,
                min_gap=5,
            ),
            modifier_limits=ModifierLimits(
                ability_min=ABILITY_MODIFIER_MIN,
                ability_max=ABILITY_MODIFIER_MAX,
                skill_min=SKILL_MODIFIER_MIN,
                skill_max=SKILL_MODIFIER_MAX,
            ),
            tts_providers=tts_providers,
        )
    except Exception as e:
        logger.error(f"Could not return game data: {e}")
        raise
