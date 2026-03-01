from enum import Enum
from typing import Dict, List

from pydantic import BaseModel, Field, field_validator

from app.clients.tts import ELEVANLABS_TTS, GOOGLE_TTS
from app.db.limits import (
    CHARACTER_BACKGROUND_LIMIT,
    CHARACTER_COMMUNICATION_LIMIT,
    CHARACTER_MOTIVATION_LIMIT,
    CHARACTER_PROFESSION_LIMIT,
    NAME_LIMIT,
    PREFERENCE_VALUE_MAX,
    PREFERENCE_VALUE_MIN,
)

from .alignment import VALID_ALIGNMENTS
from .race import VALID_GENDERS, VALID_RACES, VALID_SIZES
from .util import validate_choice


class CommunicationStyle(Enum):
    NERDY = "Nerdy"
    THEATRICAL = "Theatrical"
    JOKING = "Joking"
    PARANOID = "Paranoid"
    PROFANE = "Profane"
    FLIRTATIOUS = "Flirtatious"
    CUSTOM = "Custom"


class CharacterBase(BaseModel):
    name: str = Field(..., description="Character name", max_length=NAME_LIMIT)
    race: str = Field(..., description="Character race")
    size: str = Field(..., description="Character size")
    alignment: str = Field(..., description="Character alignment")
    gender: str = Field(..., description="Character gender")
    profession: str = Field(
        ..., description="Character profession", max_length=CHARACTER_PROFESSION_LIMIT
    )
    background: str = Field(
        ..., description="Character background", max_length=CHARACTER_BACKGROUND_LIMIT
    )
    communication_style: str = Field(
        "",
        description="Character communication style summary",
        max_length=CHARACTER_COMMUNICATION_LIMIT,
    )
    communication_style_examples: List[str] | None = Field(
        None,
        description="Communication style examples",
        exclude=True,
    )
    communication_style_type: str = Field(
        ...,
        description="Communication style preset",
    )
    motivation: str = Field(
        ..., description="Character motivation", max_length=CHARACTER_MOTIVATION_LIMIT
    )
    personality: str = Field(
        "",
        description="AI-generated personality profile for influence scoring",
        exclude=True,
    )
    voice_id: str = Field(..., description="TTS provider voice Id")
    voice_name: str = Field("Default", description="TTS provider voice name")
    tts_provider: str = Field(..., description="TTS provider")

    # Bias
    race_preferences: Dict[str, int] | None = Field(
        None, description="Race preferences for influence calculation"
    )
    class_preferences: Dict[str, int] | None = Field(
        None, description="Class preferences for influence calculation"
    )
    gender_preferences: Dict[str, int] | None = Field(
        None, description="Gender preferences for influence calculation"
    )
    size_preferences: Dict[str, int] | None = Field(
        None, description="Size preferences for influence calculation"
    )

    @field_validator("tts_provider")
    @classmethod
    def validate_tts(cls, v):
        if v is not None:
            return validate_choice(v, [GOOGLE_TTS, ELEVANLABS_TTS], "TTS Provider")
        return v

    @field_validator("race")
    @classmethod
    def validate_race(cls, v):
        if v is not None:
            return validate_choice(v, VALID_RACES, "Race")
        return v

    @field_validator("size")
    @classmethod
    def validate_size(cls, v):
        if v is not None:
            return validate_choice(v, VALID_SIZES, "Size")
        return v

    @field_validator("alignment")
    @classmethod
    def validate_alignment(cls, v):
        if v is not None:
            return validate_choice(v, VALID_ALIGNMENTS, "Alignment")
        return v

    @field_validator("gender")
    @classmethod
    def validate_gender(cls, v):
        if v is not None:
            return validate_choice(v, VALID_GENDERS, "Gender")
        return v

    @field_validator(
        "race_preferences",
        "class_preferences",
        "gender_preferences",
        "size_preferences",
    )
    @classmethod
    def validate_preferences(cls, v):
        """Ensure preference values are within ±0.3 range"""
        if v is None:
            return v
        for key, value in v.items():
            if not (PREFERENCE_VALUE_MIN <= value <= PREFERENCE_VALUE_MAX):
                raise ValueError(
                    f"Preference values must be between {PREFERENCE_VALUE_MIN} and {PREFERENCE_VALUE_MAX}, got {value} for {key}"
                )
        return v


class CharacterCreate(CharacterBase):
    """Character creation model - inherits all validation from CharacterBase."""

    pass


class CharacterUpdate(CharacterBase):
    """Character update model - all fields optional with same validation rules."""

    name: str | None = None
    race: str | None = None
    size: str | None = None
    alignment: str | None = None
    gender: str | None = None
    profession: str | None = None
    background: str | None = None
    communication_style: str | None = None
    communication_style_type: str | None = None
    communication_style_examples: List[str] | None = None
    motivation: str | None = None
    personality: str | None = None
    voice_id: str | None = None
    voice_name: str | None = None
    tts_provider: str | None = None
    race_preferences: Dict[str, int] | None = None
    class_preferences: Dict[str, int] | None = None
    gender_preferences: Dict[str, int] | None = None
    size_preferences: Dict[str, int] | None = None


class Character(CharacterBase):
    id: int

    def to_prompt(self) -> str:
        """Convert character data into a comprehensive character prompt for AI interactions."""

        # Reminder that personality includes bias summaries
        return f"""# Character Identity
            You are {self.name}, a {self.race} {self.profession}. You ARE this character completely.
            **Background**: {self.background}
            **Motivation**: {self.motivation}
            **Communication Style**: {self.communication_style}
            **Personality Summary**: {self.personality}"""

    model_config = {"from_attributes": True}
