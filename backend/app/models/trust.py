from pydantic import BaseModel, field_validator
from app.models.reveal import DifficultyClass

BASE_TRUST_MIN = DifficultyClass.ALWAYS.value
BASE_TRUST_MAX = DifficultyClass.MEDIUM.value - 3  # Just below MEDIUM threshold
EARNED_TRUST_MIN = -18
EARNED_TRUST_MAX = 12
TOTAL_TRUST_MIN = DifficultyClass.ALWAYS.value
TOTAL_TRUST_MAX = DifficultyClass.NEARLY_IMPOSSIBLE.value

TRUST_CHANGE_MIN = -DifficultyClass.HARD.value
TRUST_CHANGE_MAX = DifficultyClass.HARD.value


class TrustStateBase(BaseModel):
    character_id: int
    player_id: int
    base_trust: int = 0
    earned_trust: int = 0

    @field_validator("base_trust")
    @classmethod
    def validate_base_trust(cls, v):
        if not (BASE_TRUST_MIN <= v <= BASE_TRUST_MAX):
            raise ValueError(
                f"Base trust must be between {BASE_TRUST_MIN} and {BASE_TRUST_MAX}"
            )
        return v

    @field_validator("earned_trust")
    @classmethod
    def validate_earned_trust(cls, v):
        if not (EARNED_TRUST_MIN <= v <= EARNED_TRUST_MAX):
            raise ValueError(
                f"Earned trust must be between {EARNED_TRUST_MIN} and {EARNED_TRUST_MAX}"
            )
        return v


class TrustState(TrustStateBase):
    @property
    def total_trust(self) -> int:
        """Calculate total trust, clamped between 0 and 30 DC"""
        return max(
            TOTAL_TRUST_MIN, min(TOTAL_TRUST_MAX, self.base_trust + self.earned_trust)
        )


class TrustStateCreate(TrustStateBase):
    pass
