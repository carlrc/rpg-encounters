from pydantic import BaseModel, field_validator
from typing import Optional, List
from enum import Enum
from app.models.trust import BASE_TRUST_MIN, TOTAL_TRUST_MAX


class RevealLayer(Enum):
    PUBLIC = 1
    PRIVILEGED = 2
    EXCLUSIVE = 3


REVEAL_DEFAULT_THRESHOLDS = {
    RevealLayer.PUBLIC: 0.0,  # Always accessible
    RevealLayer.PRIVILEGED: 0.55,  # Requires almost perfect static base trust
    RevealLayer.EXCLUSIVE: 0.8,  # Requires base + earned trust
}


class RevealBase(BaseModel):
    title: str
    character_ids: List[int]
    level_1_content: str  # Public level content (always required)
    level_2_content: Optional[str] = None  # Privileged level content (optional)
    level_3_content: Optional[str] = None  # Exclusive level content (optional)
    privileged_threshold: Optional[float] = (
        None  # Custom threshold for privileged content
    )
    exclusive_threshold: Optional[float] = (
        None  # Custom threshold for exclusive content
    )

    @field_validator("privileged_threshold", "exclusive_threshold")
    @classmethod
    def validate_thresholds(cls, v):
        if v is not None and not (BASE_TRUST_MIN <= v <= TOTAL_TRUST_MAX):
            raise ValueError(
                f"Thresholds must be between {BASE_TRUST_MIN} and {TOTAL_TRUST_MAX}"
            )
        return v

    def get_threshold(self, layer: RevealLayer) -> float:
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
