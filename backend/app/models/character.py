from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from enum import Enum

class CharacterRace(Enum):
    HUMAN = 'Human'
    ELF = 'Elf'
    DWARF = 'Dwarf'
    HALFLING = 'Halfling'
    DRAGONBORN = 'Dragonborn'
    GNOME = 'Gnome'
    HALF_ELF = 'Half-Elf'
    HALF_ORC = 'Half-Orc'
    TIEFLING = 'Tiefling'

class CharacterSize(Enum):
    SMALL = 'Small'
    MEDIUM = 'Medium'

class CharacterAlignment(Enum):
    LAWFUL_GOOD = 'Lawful Good'
    NEUTRAL_GOOD = 'Neutral Good'
    CHAOTIC_GOOD = 'Chaotic Good'
    LAWFUL_NEUTRAL = 'Lawful Neutral'
    TRUE_NEUTRAL = 'True Neutral'
    CHAOTIC_NEUTRAL = 'Chaotic Neutral'
    LAWFUL_EVIL = 'Lawful Evil'
    NEUTRAL_EVIL = 'Neutral Evil'
    CHAOTIC_EVIL = 'Chaotic Evil'

# Constants for backward compatibility and validation
VALID_RACES = [race.value for race in CharacterRace]
VALID_SIZES = [size.value for size in CharacterSize]
VALID_ALIGNMENTS = [alignment.value for alignment in CharacterAlignment]

# Character field limits
CHARACTER_BACKGROUND_LIMIT = 240
CHARACTER_COMMUNICATION_LIMIT = 180
CHARACTER_MOTIVATION_LIMIT = 300

# Shared validation functions
def validate_character_count(text: str, max_characters: int, field_name: str) -> str:
    """Validate character count for text fields."""
    if text:
        character_count = len(text)
        if character_count > max_characters:
            raise ValueError(f'{field_name} must be {max_characters} characters or less')
    return text

def validate_choice(value: str, valid_choices: List[str], field_name: str) -> str:
    """Validate that a value is in the list of valid choices."""
    if value not in valid_choices:
        raise ValueError(f'{field_name} must be one of: {", ".join(valid_choices)}')
    return value


class CharacterBase(BaseModel):
    name: str
    avatar: Optional[str] = Field(None, description="Character avatar image (base64 or URL)")
    race: str = Field(..., description="Character race")
    size: str = Field(..., description="Character size")
    alignment: str = Field(..., description="Character alignment")
    profession: str = Field(..., description="Character profession")
    background: str = Field(..., description="Character background")
    communication_style: str = Field(..., description="Character communication style")
    motivation: str = Field(..., description="Character motivation")

    @field_validator('background')
    @classmethod
    def validate_background_character_count(cls, v):
        if v is not None:
            return validate_character_count(v, CHARACTER_BACKGROUND_LIMIT, 'Background')
        return v

    @field_validator('communication_style')
    @classmethod
    def validate_communication_style_character_count(cls, v):
        if v is not None:
            return validate_character_count(v, CHARACTER_COMMUNICATION_LIMIT, 'Communication style')
        return v

    @field_validator('motivation')
    @classmethod
    def validate_motivation_character_count(cls, v):
        if v is not None:
            return validate_character_count(v, CHARACTER_MOTIVATION_LIMIT, 'Motivation')
        return v

    @field_validator('race')
    @classmethod
    def validate_race(cls, v):
        if v is not None:
            return validate_choice(v, VALID_RACES, 'Race')
        return v

    @field_validator('size')
    @classmethod
    def validate_size(cls, v):
        if v is not None:
            return validate_choice(v, VALID_SIZES, 'Size')
        return v

    @field_validator('alignment')
    @classmethod
    def validate_alignment(cls, v):
        if v is not None:
            return validate_choice(v, VALID_ALIGNMENTS, 'Alignment')
        return v

class CharacterCreate(CharacterBase):
    """Character creation model - inherits all validation from CharacterBase."""
    pass

class CharacterUpdate(CharacterBase):
    """Character update model - all fields optional with same validation rules."""
    name: Optional[str] = None
    race: Optional[str] = None
    size: Optional[str] = None
    alignment: Optional[str] = None
    profession: Optional[str] = None
    background: Optional[str] = None
    communication_style: Optional[str] = None
    motivation: Optional[str] = None

class Character(CharacterBase):
    id: int
    
    def to_prompt(self) -> str:
        """Convert character data into a system prompt for AI interactions."""
        
        return f"""
        # Character Background Prompt
        
        You are {self.name}, a {self.race} and your job is {self.profession}. Stay in character and respond naturally as {self.name} would.

        ## Core Directives

        NARRATIVE-DRIVEN: All communication should reference your motivation and memories
        INTERACTIONS: Consider the player communication with you (e.g., race, appearance) in your responses

        ## Response Guidelines
        ### Background
        {self.background} 

        ### Motivation
        {self.motivation}

        ### Communication Style
         {self.communication_style}

        """
    
    model_config = {"from_attributes": True}
