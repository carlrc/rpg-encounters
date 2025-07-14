from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Union
from enum import Enum

class VisibilityType(str, Enum):
    ALWAYS = "always"
    KEYWORD = "keyword"
    PLAYER_RACE = "player_race"
    PLAYER_ALIGNMENT = "player_alignment"
    TAGS = "tags"

# Shared validation functions
def validate_memory_text_length(memory_text, info):
    if memory_text is not None:
        # Get character_limit from the same instance if available
        character_limit = info.data.get('character_limit', 500) if info.data else 500
        
        if len(memory_text) > character_limit:
            raise ValueError(f'Memory text must be {character_limit} characters or less')
    return memory_text

def validate_character_limit_range(character_limit):
    if character_limit is not None:
        if character_limit < 1:
            raise ValueError('Character limit must be at least 1')
        if character_limit > 10000:
            raise ValueError('Character limit cannot exceed 10,000')
    return character_limit

def validate_player_races_list(races_list):
    if races_list is not None:
        valid_races = [
            'Human', 'Elf', 'Dwarf', 'Halfling', 'Dragonborn', 
            'Gnome', 'Half-Elf', 'Half-Orc', 'Tiefling'
        ]
        for race in races_list:
            if race not in valid_races:
                raise ValueError(f'Invalid race: {race}. Must be one of: {", ".join(valid_races)}')
    return races_list

def validate_player_alignments_list(alignments_list):
    if alignments_list is not None:
        valid_alignments = [
            'Lawful Good', 'Neutral Good', 'Chaotic Good',
            'Lawful Neutral', 'True Neutral', 'Chaotic Neutral',
            'Lawful Evil', 'Neutral Evil', 'Chaotic Evil'
        ]
        for alignment in alignments_list:
            if alignment not in valid_alignments:
                raise ValueError(f'Invalid alignment: {alignment}. Must be one of: {", ".join(valid_alignments)}')
    return alignments_list

def validate_string_lists(string_list):
    if string_list is not None:
        # Remove empty strings and strip whitespace
        return [item.strip() for item in string_list if item.strip()]
    return string_list

class MemoryBase(BaseModel):
    title: str = Field(..., description="Memory title")
    linked_character_ids: List[int] = Field(default_factory=list, description="IDs of linked characters")
    visibility_type: VisibilityType = Field(default=VisibilityType.ALWAYS, description="Visibility condition type")
    keywords: List[str] = Field(default_factory=list, description="Keywords for keyword-based visibility")
    player_races: List[str] = Field(default_factory=list, description="Player races for race-based visibility")
    player_alignments: List[str] = Field(default_factory=list, description="Player alignments for alignment-based visibility")
    player_tags: List[str] = Field(default_factory=list, description="Player tags for tag-based visibility")
    memory_text: str = Field(..., description="Memory content text")
    character_limit: int = Field(default=500, description="Character limit for memory text")

    @field_validator('memory_text')
    @classmethod
    def validate_memory_text(cls, v, info):
        return validate_memory_text_length(v, info)

    @field_validator('character_limit')
    @classmethod
    def validate_character_limit(cls, v):
        return validate_character_limit_range(v)

    @field_validator('player_races')
    @classmethod
    def validate_player_races(cls, v):
        return validate_player_races_list(v)

    @field_validator('player_alignments')
    @classmethod
    def validate_player_alignments(cls, v):
        return validate_player_alignments_list(v)

    @field_validator('keywords', 'player_tags')
    @classmethod
    def validate_string_fields(cls, v):
        return validate_string_lists(v)

class MemoryCreate(MemoryBase):
    pass

class MemoryUpdate(BaseModel):
    title: Optional[str] = None
    linked_character_ids: Optional[List[int]] = None
    visibility_type: Optional[VisibilityType] = None
    keywords: Optional[List[str]] = None
    player_races: Optional[List[str]] = None
    player_alignments: Optional[List[str]] = None
    player_tags: Optional[List[str]] = None
    memory_text: Optional[str] = None
    character_limit: Optional[int] = None

    @field_validator('memory_text')
    @classmethod
    def validate_memory_text(cls, v, info):
        return validate_memory_text_length(v, info)

    @field_validator('character_limit')
    @classmethod
    def validate_character_limit(cls, v):
        return validate_character_limit_range(v)

    @field_validator('player_races')
    @classmethod
    def validate_player_races(cls, v):
        return validate_player_races_list(v)

    @field_validator('player_alignments')
    @classmethod
    def validate_player_alignments(cls, v):
        return validate_player_alignments_list(v)

    @field_validator('keywords', 'player_tags')
    @classmethod
    def validate_string_fields(cls, v):
        return validate_string_lists(v)

class Memory(MemoryBase):
    id: int
    
    class Config:
        from_attributes = True
