from enum import Enum
from typing import List

from pydantic import BaseModel, field_validator


class RevealLayer(Enum):
    NEGATIVE = 0
    STANDARD = 1
    PRIVILEGED = 2
    EXCLUSIVE = 3


class DifficultyClass(Enum):
    ALWAYS = 0
    VERY_EASY = 5
    EASY = 10
    MEDIUM = 15
    HARD = 20
    VERY_HARD = 25
    NEARLY_IMPOSSIBLE = 30


REVEAL_DEFAULT_THRESHOLDS = {
    RevealLayer.STANDARD: DifficultyClass.ALWAYS.value,
    RevealLayer.PRIVILEGED: DifficultyClass.MEDIUM.value,
    RevealLayer.EXCLUSIVE: DifficultyClass.HARD.value,
}


class RevealBase(BaseModel):
    title: str
    character_ids: List[int]
    level_1_content: str  # Standard level content
    level_2_content: str | None = None  # Privileged level content
    level_3_content: str | None = None  # Exclusive level content
    privileged_threshold: int | None = None  # Threshold for privileged content
    exclusive_threshold: int | None = None  # Threshold for exclusive content

    @field_validator("privileged_threshold", "exclusive_threshold")
    @classmethod
    def validate_thresholds(cls, v):
        if v is not None and not (
            DifficultyClass.ALWAYS.value <= v <= DifficultyClass.NEARLY_IMPOSSIBLE.value
        ):
            raise ValueError(
                f"Thresholds must be between {DifficultyClass.ALWAYS.value} and {DifficultyClass.NEARLY_IMPOSSIBLE.value}"
            )
        return v

    def get_threshold(self, layer: RevealLayer) -> int:
        """Get the effective threshold for a reveal layer, with fallback to defaults"""
        if self.exclusive_threshold is not None and layer == RevealLayer.EXCLUSIVE:
            return self.exclusive_threshold
        elif self.privileged_threshold is not None and layer == RevealLayer.PRIVILEGED:
            return self.privileged_threshold
        else:
            return REVEAL_DEFAULT_THRESHOLDS[layer]


class Reveal(RevealBase):
    id: int


class RevealCreate(RevealBase):
    pass
