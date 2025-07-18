from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict
from enum import Enum

BASE_TRUST_MIN = 0.0
BASE_TRUST_MAX = 0.6
EARNED_TRUST_MIN = -0.6
EARNED_TRUST_MAX = 0.4
TOTAL_TRUST_MIN = 0.0
TOTAL_TRUST_MAX = 1.0

TRUST_CHANGE_MIN = -0.3
TRUST_CHANGE_MAX = 0.3
PREFERENCE_VALUE_MIN = -0.3
PREFERENCE_VALUE_MAX = 0.3

TRUST_THRESHOLDS = {
    'PUBLIC': BASE_TRUST_MIN,      # 0.0 - Always accessible
    'PRIVILEGED': 0.55,            # 0.55 - Requires almost perfect static (92% of max base trust)
    'EXCLUSIVE': 0.8               # 0.8 - Requires base + earned trust (dynamic)
}

# Shared validation functions
def validate_preference_values(preferences: Dict[str, float]) -> Dict[str, float]:
    """Ensure preference values are within ±0.3 range"""
    for key, value in preferences.items():
        if not (PREFERENCE_VALUE_MIN <= value <= PREFERENCE_VALUE_MAX):
            raise ValueError(f'Preference values must be between {PREFERENCE_VALUE_MIN} and {PREFERENCE_VALUE_MAX}, got {value} for {key}')
    return preferences

def validate_trust_range(trust_value: float) -> float:
    """Ensure trust is within 0.0 to 1.0 range"""
    if not (TOTAL_TRUST_MIN <= trust_value <= TOTAL_TRUST_MAX):
        raise ValueError(f'Trust must be between {TOTAL_TRUST_MIN} and {TOTAL_TRUST_MAX}')
    return trust_value

def get_trust_threshold(layer: 'NuggetLayer') -> float:
    """Get the trust threshold required for a nugget layer"""
    threshold_map = {
        NuggetLayer.PUBLIC: TRUST_THRESHOLDS['PUBLIC'],
        NuggetLayer.PRIVILEGED: TRUST_THRESHOLDS['PRIVILEGED'],
        NuggetLayer.EXCLUSIVE: TRUST_THRESHOLDS['EXCLUSIVE']
    }
    return threshold_map[layer]

def can_access_nugget(trust_level: float, layer: 'NuggetLayer') -> bool:
    """Check if a trust level can access a nugget layer"""
    return trust_level >= get_trust_threshold(layer)

class NuggetLayer(Enum):
    PUBLIC = 1      # 0.0+ (always accessible)
    PRIVILEGED = 2  # 0.55+ (requires almost perfect static configuration)  
    EXCLUSIVE = 3   # 0.8+ (requires base + earned trust)

class TrustNugget(BaseModel):
    id: int
    title: str
    character_ids: List[int]
    level_1_content: str  # Public level content
    level_2_content: str  # Privileged level content
    level_3_content: str  # Exclusive level content

class TrustNuggetCreate(BaseModel):
    title: str
    character_ids: List[int]
    level_1_content: str
    level_2_content: str
    level_3_content: str

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
    base_trust: float = 0.0      # Static trust from characteristics (0.0 to 0.6)
    earned_trust: float = 0.0    # Dynamic trust from interactions (-0.6 to +0.4)
    
    @property
    def total_trust(self) -> float:
        """Calculate total trust, clamped between 0.0 and 1.0"""
        return max(0.0, min(1.0, self.base_trust + self.earned_trust))

    @field_validator('base_trust')
    @classmethod
    def validate_base_trust(cls, v):
        if not (BASE_TRUST_MIN <= v <= BASE_TRUST_MAX):
            raise ValueError(f'Base trust must be between {BASE_TRUST_MIN} and {BASE_TRUST_MAX}')
        return v
    
    @field_validator('earned_trust')
    @classmethod
    def validate_earned_trust(cls, v):
        if not (EARNED_TRUST_MIN <= v <= EARNED_TRUST_MAX):
            raise ValueError(f'Earned trust must be between {EARNED_TRUST_MIN} and {EARNED_TRUST_MAX}')
        return v

class TrustStateCreate(BaseModel):
    character_id: int
    player_id: int
    base_trust: float = 0.0
    earned_trust: float = 0.0

    @field_validator('base_trust')
    @classmethod
    def validate_base_trust(cls, v):
        if not (BASE_TRUST_MIN <= v <= BASE_TRUST_MAX):
            raise ValueError(f'Base trust must be between {BASE_TRUST_MIN} and {BASE_TRUST_MAX}')
        return v
    
    @field_validator('earned_trust')
    @classmethod
    def validate_earned_trust(cls, v):
        if not (EARNED_TRUST_MIN <= v <= EARNED_TRUST_MAX):
            raise ValueError(f'Earned trust must be between {EARNED_TRUST_MIN} and {EARNED_TRUST_MAX}')
        return v
