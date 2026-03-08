from typing import Dict

from pydantic import BaseModel, Field, field_validator

from app.db.limits import NAME_LIMIT, PLAYER_APPEARANCE_MAX_LIMIT

from .alignment import VALID_ALIGNMENTS
from .class_traits import (
    ABILITY_MODIFIER_MAX,
    ABILITY_MODIFIER_MIN,
    SKILL_MODIFIER_MAX,
    SKILL_MODIFIER_MIN,
    VALID_ABILITIES,
    VALID_CLASSES,
    VALID_SKILLS,
)
from .race import VALID_GENDERS, VALID_RACES, VALID_SIZES
from .util import validate_choice


class PlayerBase(BaseModel):
    name: str = Field(..., description="Player name", max_length=NAME_LIMIT)
    rl_name: str = Field(
        ..., description="Real-life player name", max_length=NAME_LIMIT
    )
    appearance: str = Field(
        ..., description="Player appearance", max_length=PLAYER_APPEARANCE_MAX_LIMIT
    )
    race: str = Field(..., description="Player race")
    class_name: str = Field(..., description="Player class")
    size: str = Field(..., description="Player size")
    alignment: str = Field(..., description="Player alignment")
    gender: str = Field(..., description="Player gender")
    abilities: Dict[str, int] = Field(..., description="Abilities of the player")
    skills: Dict[str, int] = Field(..., description="Skills of the player")

    @field_validator("race")
    @classmethod
    def validate_race(cls, v):
        if v is not None:
            return validate_choice(v, VALID_RACES, "Race")
        return v

    @field_validator("class_name")
    @classmethod
    def validate_class(cls, v):
        if v is not None:
            return validate_choice(v, VALID_CLASSES, "Class")
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

    @field_validator("abilities")
    @classmethod
    def validate_abilities(cls, v):
        """Ensure abilities values are within range"""
        if v is None:
            return v
        for key, value in v.items():
            validate_choice(key, VALID_ABILITIES, "Ability")
            if not (ABILITY_MODIFIER_MIN <= value <= ABILITY_MODIFIER_MAX):
                raise ValueError(
                    f"Abilities must be between {ABILITY_MODIFIER_MIN} and {ABILITY_MODIFIER_MAX}. Got {value} for {key}"
                )
        return v

    @field_validator("skills")
    @classmethod
    def validate_skills(cls, v):
        """Ensure skills values are within range"""
        if v is None:
            return v
        for key, value in v.items():
            validate_choice(key, VALID_SKILLS, "Skill")
            if not (SKILL_MODIFIER_MIN <= value <= SKILL_MODIFIER_MAX):
                raise ValueError(
                    f"Skills must be between {SKILL_MODIFIER_MIN} and {SKILL_MODIFIER_MAX}. Got {value} for {key}"
                )
        return v


class PlayerCreate(PlayerBase):
    pass


class PlayerUpdate(PlayerBase):
    """Player update model - all fields optional with same validation rules."""

    name: str | None = None
    rl_name: str | None = None
    appearance: str | None = None
    race: str | None = None
    class_name: str | None = None
    size: str | None = None
    alignment: str | None = None
    gender: str | None = None
    abilities: Dict[str, int] | None = None
    skills: Dict[str, int] | None = None


class Player(PlayerBase):
    id: int

    model_config = {"from_attributes": True}
