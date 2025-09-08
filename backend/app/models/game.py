from typing import Dict, List

from pydantic import BaseModel, Field


class ValidationLimits(BaseModel):
    """Character and text limits for form validation"""

    name: int = Field(..., description="Character name limit")
    player_appearance: int = Field(
        ..., description="Player appearance description limit"
    )
    character_profession: int = Field(..., description="Character profession limit")
    character_background: int = Field(..., description="Character background limit")
    character_communication: int = Field(
        ..., description="Character communication style limit"
    )
    character_motivation: int = Field(..., description="Character motivation limit")
    memory_title: int = Field(..., description="Memory title limit")
    memory_content: int = Field(..., description="Memory content limit")
    reveal_title: int = Field(..., description="Reveal title limit")
    reveal_content: int = Field(..., description="Reveal content limit")


class ThresholdLimits(BaseModel):
    """Threshold configuration limits for reveals"""

    min: int = Field(..., description="Minimum threshold value")
    max: int = Field(..., description="Maximum threshold value")
    step: int = Field(..., description="Step increment for threshold values")
    min_gap: int = Field(..., description="Minimum gap between threshold levels")


class SizeOptions(BaseModel):
    """Size options for different entity types"""

    player: List[str] = Field(..., description="Valid sizes for players")
    character: List[str] = Field(..., description="Valid sizes for characters")


class DefaultThresholds(BaseModel):
    """Default threshold values for reveal layers"""

    standard: int = Field(..., description="Standard reveal threshold")
    privileged: int = Field(..., description="Privileged reveal threshold")
    exclusive: int = Field(..., description="Exclusive reveal threshold")


class GameDataResponse(BaseModel):
    """Complete game data response containing all constants for frontend caching"""

    races: List[str] = Field(..., description="Available character races")
    classes: List[str] = Field(..., description="Available character classes")
    alignments: List[str] = Field(..., description="Available character alignments")
    skills: List[str] = Field(..., description="Available character skills")
    communication_styles: List[str] = Field(
        ..., description="Available communication styles"
    )
    sizes: SizeOptions = Field(..., description="Size options for different entities")
    difficulty_classes: Dict[str, int] = Field(
        ..., description="Difficulty class values"
    )
    default_thresholds: DefaultThresholds = Field(
        ..., description="Default reveal thresholds"
    )
    validation_limits: ValidationLimits = Field(
        ..., description="Text and character limits"
    )
    threshold_limits: ThresholdLimits = Field(
        ..., description="Threshold configuration limits"
    )
    tts_providers: List[str] = Field(..., description="Available TTS providers")
