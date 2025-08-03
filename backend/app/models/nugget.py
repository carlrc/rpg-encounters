from pydantic import BaseModel
from typing import Optional, List
from enum import Enum


class NuggetLayer(Enum):
    PUBLIC = 1  # 0.0+ (always accessible)
    PRIVILEGED = 2  # 0.55+ (requires almost perfect static configuration)
    EXCLUSIVE = 3  # 0.8+ (requires base + earned trust)


NUGGET_THRESHOLDS = {
    NuggetLayer.PUBLIC.name: 0.0,  # Always accessible
    NuggetLayer.PRIVILEGED.name: 0.55,  # Requires almost perfect static (92% of max base trust)
    NuggetLayer.EXCLUSIVE.name: 0.8,  # Requires base + earned trust (dynamic)
}


class TrustNuggetBase(BaseModel):
    title: str
    character_ids: List[int]
    level_1_content: str  # Public level content (always required)
    level_2_content: Optional[str] = None  # Privileged level content (optional)
    level_3_content: Optional[str] = None  # Exclusive level content (optional)


class TrustNugget(TrustNuggetBase):
    id: int


class TrustNuggetCreate(TrustNuggetBase):
    pass
