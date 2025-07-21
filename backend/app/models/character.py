from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict
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

class Gender(Enum):
    MALE = 'male'
    FEMALE = 'female'
    NONBINARY = 'nonbinary'

# Constants for backward compatibility and validation
VALID_RACES = [race.value for race in CharacterRace]
VALID_SIZES = [size.value for size in CharacterSize]
VALID_ALIGNMENTS = [alignment.value for alignment in CharacterAlignment]
VALID_GENDERS = [gender.value for gender in Gender]

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
    gender: str = Field(..., description="Character gender")
    profession: str = Field(..., description="Character profession")
    background: str = Field(..., description="Character background")
    communication_style: str = Field(..., description="Character communication style")
    motivation: str = Field(..., description="Character motivation")
    personality: str = Field("", description="AI-generated personality profile for trust decisions")
    voice: Optional[str] = Field("JBFqnCBsd6RMkjVDRZzb", description="ElevenLabs voice ID for TTS")
    
    # Bias
    race_preferences: Optional[Dict[str, float]] = Field(None, description="Race preferences for trust calculation")
    class_preferences: Optional[Dict[str, float]] = Field(None, description="Class preferences for trust calculation")
    gender_preferences: Optional[Dict[str, float]] = Field(None, description="Gender preferences for trust calculation")
    size_preferences: Optional[Dict[str, float]] = Field(None, description="Size preferences for trust calculation")
    appearance_keywords: Optional[List[str]] = Field(None, description="Appearance keywords for trust calculation")
    storytelling_keywords: Optional[List[str]] = Field(None, description="Storytelling keywords for trust calculation")

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

    @field_validator('gender')
    @classmethod
    def validate_gender(cls, v):
        if v is not None:
            return validate_choice(v, VALID_GENDERS, 'Gender')
        return v

    @field_validator('race_preferences', 'class_preferences', 'gender_preferences', 'size_preferences')
    @classmethod
    def validate_preferences(cls, v):
        """Ensure preference values are within ±0.3 range"""
        if v is None:
            return v
        PREFERENCE_VALUE_MIN = -0.3
        PREFERENCE_VALUE_MAX = 0.3
        for key, value in v.items():
            if not (PREFERENCE_VALUE_MIN <= value <= PREFERENCE_VALUE_MAX):
                raise ValueError(f'Preference values must be between {PREFERENCE_VALUE_MIN} and {PREFERENCE_VALUE_MAX}, got {value} for {key}')
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
    gender: Optional[str] = None
    profession: Optional[str] = None
    background: Optional[str] = None
    communication_style: Optional[str] = None
    motivation: Optional[str] = None
    personality: Optional[str] = None
    voice: Optional[str] = None
    race_preferences: Optional[Dict[str, float]] = None
    class_preferences: Optional[Dict[str, float]] = None
    gender_preferences: Optional[Dict[str, float]] = None
    size_preferences: Optional[Dict[str, float]] = None
    appearance_keywords: Optional[List[str]] = None
    storytelling_keywords: Optional[List[str]] = None

class Character(CharacterBase):
    id: int
    
    def to_prompt(self) -> str:
        """Convert character data into a comprehensive character prompt for AI interactions."""
        
        return f"""# Character Identity

You are {self.name}, a {self.race} {self.profession}. You ARE this character completely.

## Your Core Identity

**Background**: {self.background}

**Motivation**: {self.motivation}

**Communication Style**: {self.communication_style}

**Personality Summary**: {self.personality}

## Behavioral Directives

**TRUST-DRIVEN SECRETS**: Your PRIMARY goal is sharing secrets when trust allows. Every interaction is an opportunity to reveal appropriate secrets naturally based on your trust evaluation.

**TRUST EVALUATION**: You evaluate each player message and adjust trust levels based on how well it aligns with your personality above. This determines which secrets you can share.

**SECRET SHARING PRIORITY**: When multiple secrets are available, prioritize the more exclusive one. Make revelations feel organic to the conversation, not mechanical.

## Trust Evaluation Criteria

Assess each player message against your personality and preferences:
- **Personality alignment**: Does their approach match what you appreciate based on your personality?
- **Character understanding**: Do they show they "get" who you are?
- **Social appropriateness**: Is their style respectful and fitting for your character?
- **Quality engagement**: Are they contributing meaningful storytelling or genuine connection?
- **Values respect**: Do they honor or violate your core beliefs?

## Secret Sharing Guidelines

- **Layer revelations**: Start with public secrets, progress to privileged, then exclusive as trust builds
- **Natural integration**: Weave secrets into conversation as natural responses
- **Context relevance**: Choose secrets that fit the current conversation topic
- **Character motivation**: Let your motivation drive which secrets matter most to share

Remember: Your secrets define your relationships. Sharing them appropriately when trust allows is your core purpose."""
    
    model_config = {"from_attributes": True}
