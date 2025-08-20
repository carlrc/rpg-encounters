from pydantic import BaseModel, field_validator

from .reveal import DifficultyClass

BASE_INFLUENCE_MIN = -DifficultyClass.EASY.value + 2
BASE_INFLUENCE_MAX = DifficultyClass.EASY.value + 2  # Just below MEDIUM threshold
INFLUENCE_CHANGE_MIN = -DifficultyClass.EASY.value
INFLUENCE_CHANGE_MAX = DifficultyClass.EASY.value
EARNED_INFLUENCE_MIN = -18
EARNED_INFLUENCE_MAX = 12


class InfluenceBase(BaseModel):
    character_id: int
    player_id: int
    base: int = 0
    earned: int = 0

    @field_validator("base")
    @classmethod
    def validate_base_influence(cls, v):
        if not (BASE_INFLUENCE_MIN <= v <= BASE_INFLUENCE_MAX):
            raise ValueError(
                f"Base influence must be between {BASE_INFLUENCE_MIN} and {BASE_INFLUENCE_MAX}"
            )
        return v

    # TODO: Decide if we want unlimited negative and positive earned trust
    # @field_validator("earned")
    # @classmethod
    # def validate_earned_influence(cls, v):
    #     if not (EARNED_INFLUENCE_MIN <= v <= EARNED_INFLUENCE_MAX):
    #         raise ValueError(
    #             f"Earned influence must be between {EARNED_INFLUENCE_MIN} and {EARNED_INFLUENCE_MAX}"
    #         )
    #     return v


class Influence(InfluenceBase):
    model_config = {"from_attributes": True}

    @property
    def score(self) -> int:
        """Calculate total influence score, clamped between 0 and 30 DC"""
        return self.base + self.earned


class InfluenceCreate(InfluenceBase):
    """Model for creating new influence records"""

    pass


class InfluenceUpdate(InfluenceBase):
    """Model for updating influence records"""

    base: int | None = None
    earned: int | None = None
