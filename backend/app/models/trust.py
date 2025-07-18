from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict
from enum import Enum

# Shared validation functions
def validate_preference_values(preferences: Dict[str, float]) -> Dict[str, float]:
    """Ensure preference values are within ±0.3 range"""
    for key, value in preferences.items():
        if not (-0.3 <= value <= 0.3):
            raise ValueError(f'Preference values must be between -0.3 and 0.3, got {value} for {key}')
    return preferences

def validate_trust_range(trust_value: float) -> float:
    """Ensure trust is within 0.0 to 1.0 range"""
    if not (0.0 <= trust_value <= 1.0):
        raise ValueError('Trust must be between 0.0 and 1.0')
    return trust_value

class NuggetLayer(Enum):
    PUBLIC = 1      # 0.0 - 0.33
    PRIVILEGED = 2  # 0.34 - 0.66  
    EXCLUSIVE = 3   # 0.67 - 1.0

class TrustNugget(BaseModel):
    id: int
    character_id: int
    layer: NuggetLayer
    content: str

class TrustNuggetCreate(BaseModel):
    character_id: int
    layer: NuggetLayer
    content: str

class TrustProfile(BaseModel):
    character_id: int
    race_preferences: Dict[str, float] = Field(default_factory=dict)      # {"Human": 0.3, "Elf": -0.3}
    class_preferences: Dict[str, float] = Field(default_factory=dict)     
    gender_preferences: Dict[str, float] = Field(default_factory=dict)    
    alignment_preferences: Dict[str, float] = Field(default_factory=dict) 
    size_preferences: Dict[str, float] = Field(default_factory=dict)      
    appearance_keywords: List[str] = Field(default_factory=list)          
    storytelling_keywords: List[str] = Field(default_factory=list)        

    @field_validator('race_preferences', 'class_preferences', 'gender_preferences', 'alignment_preferences', 'size_preferences')
    @classmethod
    def validate_preferences(cls, v):
        return validate_preference_values(v)

class TrustProfileCreate(BaseModel):
    character_id: int
    race_preferences: Dict[str, float] = Field(default_factory=dict)
    class_preferences: Dict[str, float] = Field(default_factory=dict)
    gender_preferences: Dict[str, float] = Field(default_factory=dict)
    alignment_preferences: Dict[str, float] = Field(default_factory=dict)
    size_preferences: Dict[str, float] = Field(default_factory=dict)
    appearance_keywords: List[str] = Field(default_factory=list)
    storytelling_keywords: List[str] = Field(default_factory=list)

    @field_validator('race_preferences', 'class_preferences', 'gender_preferences', 'alignment_preferences', 'size_preferences')
    @classmethod
    def validate_preferences(cls, v):
        return validate_preference_values(v)

class TrustState(BaseModel):
    character_id: int
    player_id: int
    current_trust: float = 0.0  # Just one number - that's it

    @field_validator('current_trust')
    @classmethod
    def validate_trust(cls, v):
        return validate_trust_range(v)

class TrustStateCreate(BaseModel):
    character_id: int
    player_id: int
    current_trust: float = 0.0

    @field_validator('current_trust')
    @classmethod
    def validate_trust(cls, v):
        return validate_trust_range(v)
