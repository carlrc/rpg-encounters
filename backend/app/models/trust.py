from pydantic import BaseModel, field_validator

BASE_TRUST_MIN = 0.0
BASE_TRUST_MAX = 0.6
EARNED_TRUST_MIN = -0.6
EARNED_TRUST_MAX = 0.4
TOTAL_TRUST_MIN = 0.0
TOTAL_TRUST_MAX = 1.0

TRUST_CHANGE_MIN = -0.3
TRUST_CHANGE_MAX = 0.3

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
