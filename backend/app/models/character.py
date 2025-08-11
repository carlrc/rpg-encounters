from pydantic import BaseModel, Field, field_validator
from typing import List, Dict
from enum import Enum
from app.models.reveal import DifficultyClass


class CharacterRace(Enum):
    HUMAN = "Human"
    ELF = "Elf"
    DWARF = "Dwarf"
    HALFLING = "Halfling"
    DRAGONBORN = "Dragonborn"
    GNOME = "Gnome"
    HALF_ELF = "Half-Elf"
    HALF_ORC = "Half-Orc"
    TIEFLING = "Tiefling"


class CharacterSize(Enum):
    SMALL = "Small"
    MEDIUM = "Medium"


class CharacterAlignment(Enum):
    LAWFUL_GOOD = "Lawful Good"
    NEUTRAL_GOOD = "Neutral Good"
    CHAOTIC_GOOD = "Chaotic Good"
    LAWFUL_NEUTRAL = "Lawful Neutral"
    TRUE_NEUTRAL = "True Neutral"
    CHAOTIC_NEUTRAL = "Chaotic Neutral"
    LAWFUL_EVIL = "Lawful Evil"
    NEUTRAL_EVIL = "Neutral Evil"
    CHAOTIC_EVIL = "Chaotic Evil"


class Gender(Enum):
    MALE = "male"
    FEMALE = "female"
    NONBINARY = "nonbinary"


# Constants for backward compatibility and validation
VALID_RACES = [race.value for race in CharacterRace]
VALID_SIZES = [size.value for size in CharacterSize]
VALID_ALIGNMENTS = [alignment.value for alignment in CharacterAlignment]
VALID_GENDERS = [gender.value for gender in Gender]

# Character field limits
CHARACTER_BACKGROUND_LIMIT = 240
CHARACTER_COMMUNICATION_LIMIT = 180
CHARACTER_MOTIVATION_LIMIT = 300
PREFERENCE_VALUE_MIN = -DifficultyClass.VERY_EASY.value
PREFERENCE_VALUE_MAX = DifficultyClass.VERY_EASY.value


# Shared validation functions
def validate_character_count(text: str, max_characters: int, field_name: str) -> str:
    """Validate character count for text fields."""
    if text:
        character_count = len(text)
        if character_count > max_characters:
            raise ValueError(
                f"{field_name} must be {max_characters} characters or less"
            )
    return text


def validate_choice(value: str, valid_choices: List[str], field_name: str) -> str:
    """Validate that a value is in the list of valid choices."""
    if value not in valid_choices:
        raise ValueError(f'{field_name} must be one of: {", ".join(valid_choices)}')
    return value


class CharacterBase(BaseModel):
    name: str
    avatar: str | None = Field(
        None, description="Character avatar image (base64 or URL)"
    )
    race: str = Field(..., description="Character race")
    size: str = Field(..., description="Character size")
    alignment: str = Field(..., description="Character alignment")
    gender: str = Field(..., description="Character gender")
    profession: str = Field(..., description="Character profession")
    background: str = Field(..., description="Character background")
    communication_style: str = Field(..., description="Character communication style")
    motivation: str = Field(..., description="Character motivation")
    personality: str = Field(
        "", description="AI-generated personality profile for trust decisions"
    )
    voice: str | None = Field(
        "JBFqnCBsd6RMkjVDRZzb", description="ElevenLabs voice ID for TTS"
    )

    # Bias
    race_preferences: Dict[str, int] | None = Field(
        None, description="Race preferences for trust calculation"
    )
    class_preferences: Dict[str, int] | None = Field(
        None, description="Class preferences for trust calculation"
    )
    gender_preferences: Dict[str, int] | None = Field(
        None, description="Gender preferences for trust calculation"
    )
    size_preferences: Dict[str, int] | None = Field(
        None, description="Size preferences for trust calculation"
    )
    appearance_keywords: List[str] | None = Field(
        None, description="Appearance keywords for trust calculation"
    )
    storytelling_keywords: List[str] | None = Field(
        None, description="Storytelling keywords for trust calculation"
    )

    @field_validator("background")
    @classmethod
    def validate_background_character_count(cls, v):
        if v is not None:
            return validate_character_count(v, CHARACTER_BACKGROUND_LIMIT, "Background")
        return v

    @field_validator("communication_style")
    @classmethod
    def validate_communication_style_character_count(cls, v):
        if v is not None:
            return validate_character_count(
                v, CHARACTER_COMMUNICATION_LIMIT, "Communication style"
            )
        return v

    @field_validator("motivation")
    @classmethod
    def validate_motivation_character_count(cls, v):
        if v is not None:
            return validate_character_count(v, CHARACTER_MOTIVATION_LIMIT, "Motivation")
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
    motivation: str | None = None
    personality: str | None = None
    voice: str | None = None
    race_preferences: Dict[str, int] | None = None
    class_preferences: Dict[str, int] | None = None
    gender_preferences: Dict[str, int] | None = None
    size_preferences: Dict[str, int] | None = None
    appearance_keywords: List[str] | None = None
    storytelling_keywords: List[str] | None = None


class Character(CharacterBase):
    id: int

    def to_prompt(self) -> str:
        """Convert character data into a comprehensive character prompt for AI interactions."""

        # Reminder that personality includes bias summaries
        return f"""# Character Identity
            You are {self.name}, a {self.race} {self.profession}. You ARE this character completely.
            ## Your Core Identity
            **Background**: {self.background}
            **Motivation**: {self.motivation}
            **Communication Style**: {self.communication_style}
            **Personality Summary**: {self.personality}"""

    model_config = {"from_attributes": True}
