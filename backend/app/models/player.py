from pydantic import BaseModel, Field, field_validator
from enum import Enum
from .character import CharacterRace, CharacterSize, CharacterAlignment, Gender


class PlayerClass(Enum):
    BARBARIAN = "Barbarian"
    BARD = "Bard"
    CLERIC = "Cleric"
    DRUID = "Druid"
    FIGHTER = "Fighter"
    MONK = "Monk"
    PALADIN = "Paladin"
    RANGER = "Ranger"
    ROGUE = "Rogue"
    SORCERER = "Sorcerer"
    WARLOCK = "Warlock"
    WIZARD = "Wizard"


class PlayerBase(BaseModel):
    name: str
    appearance: str = Field(..., description="Player appearance (max 40 words)")
    race: str = Field(..., description="Player race")
    class_name: str = Field(..., description="Player class")
    size: str = Field(..., description="Player size")
    alignment: str = Field(..., description="Player alignment")
    gender: str = Field(..., description="Player gender")

    @field_validator("appearance")
    @classmethod
    def validate_appearance_word_count(cls, appearance_text):
        if appearance_text:
            word_count = len(appearance_text.split())
            if word_count > 40:
                raise ValueError("Appearance must be 40 words or less")
        return appearance_text

    @field_validator("race")
    @classmethod
    def validate_race(cls, race_value):
        valid_races = [race.value for race in CharacterRace]
        if race_value not in valid_races:
            raise ValueError(f'Race must be one of: {", ".join(valid_races)}')
        return race_value

    @field_validator("class_name")
    @classmethod
    def validate_class_name(cls, class_value):
        valid_classes = [player_class.value for player_class in PlayerClass]
        if class_value not in valid_classes:
            raise ValueError(f'Class must be one of: {", ".join(valid_classes)}')
        return class_value

    @field_validator("size")
    @classmethod
    def validate_size(cls, size_value):
        valid_sizes = [size.value for size in CharacterSize]
        if size_value not in valid_sizes:
            raise ValueError(f'Size must be one of: {", ".join(valid_sizes)}')
        return size_value

    @field_validator("alignment")
    @classmethod
    def validate_alignment(cls, alignment_value):
        valid_alignments = [alignment.value for alignment in CharacterAlignment]
        if alignment_value not in valid_alignments:
            raise ValueError(f'Alignment must be one of: {", ".join(valid_alignments)}')
        return alignment_value

    @field_validator("gender")
    @classmethod
    def validate_gender(cls, gender_value):
        valid_genders = [gender.value for gender in Gender]
        if gender_value not in valid_genders:
            raise ValueError(f'Gender must be one of: {", ".join(valid_genders)}')
        return gender_value


class PlayerCreate(PlayerBase):
    pass


class PlayerUpdate(PlayerBase):
    """Player update model - all fields optional with same validation rules."""

    name: str | None = None
    appearance: str | None = None
    race: str | None = None
    class_name: str | None = None
    size: str | None = None
    alignment: str | None = None
    gender: str | None = None


class Player(PlayerBase):
    id: int

    model_config = {"from_attributes": True}
