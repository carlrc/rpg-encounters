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
    LARGE = 'Large'

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

# Shared validation functions
def validate_word_count(text: str, max_words: int, field_name: str) -> str:
    """Validate word count for text fields."""
    if text:
        word_count = len(text.split())
        if word_count > max_words:
            raise ValueError(f'{field_name} must be {max_words} words or less')
    return text

def validate_choice(value: str, valid_choices: List[str], field_name: str) -> str:
    """Validate that a value is in the list of valid choices."""
    if value not in valid_choices:
        raise ValueError(f'{field_name} must be one of: {", ".join(valid_choices)}')
    return value

def process_tags(tags_list: List[str]) -> List[str]:
    """Process tags by adding hash prefix and converting to kebab-case."""
    if not tags_list:
        return tags_list
    
    processed_tags = []
    for tag in tags_list:
        if tag and not tag.startswith('#'):
            # Auto-add hash prefix and convert to kebab-case
            kebab_case = tag.lower().replace(' ', '-').replace('_', '-')
            processed_tags.append(f'#{kebab_case}')
        else:
            processed_tags.append(tag)
    return processed_tags

class CharacterBase(BaseModel):
    name: str
    avatar: Optional[str] = Field(None, description="Character avatar image (base64 or URL)")
    race: str = Field(..., description="Character race")
    size: str = Field(..., description="Character size")
    alignment: str = Field(..., description="Character alignment")
    profession: str = Field(..., description="Character profession")
    background: str = Field(..., description="Character background (max 80 words)")
    communication_style: str = Field(..., description="Character communication style (max 30 words)")
    tags: List[str] = Field(default_factory=list, description="Character tags")

    @field_validator('background')
    @classmethod
    def validate_background_word_count(cls, v):
        if v is not None:
            return validate_word_count(v, 80, 'Background')
        return v

    @field_validator('communication_style')
    @classmethod
    def validate_communication_style_word_count(cls, v):
        if v is not None:
            return validate_word_count(v, 30, 'Communication style')
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

    @field_validator('tags')
    @classmethod
    def validate_tags(cls, v):
        if v is not None:
            return process_tags(v)
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
    tags: Optional[List[str]] = None

class Character(CharacterBase):
    id: int
    
    def to_prompt(self) -> str:
        """Convert character data into a system prompt for AI interactions."""
        
        prompt_parts = []

        prompt_parts.append(f"CHARACTER_IDENTITY=You name is {self.name}. You are a {self.size} {self.race}. Your profession is {self.profession}.")
                
        prompt_parts.append(f"CHARACTER_BACKGROUND={self.background}")
        
        prompt_parts.append(f"CHARACTER_COMMUNICATION_STYLE={self.communication_style}")
                
        return "".join(prompt_parts)
    
    class Config:
        from_attributes = True
