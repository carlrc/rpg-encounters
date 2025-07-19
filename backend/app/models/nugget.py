from pydantic import BaseModel
from typing import Optional, List
from enum import Enum

class NuggetLayer(Enum):
    PUBLIC = 1      # 0.0+ (always accessible)
    PRIVILEGED = 2  # 0.55+ (requires almost perfect static configuration)  
    EXCLUSIVE = 3   # 0.8+ (requires base + earned trust)

NUGGET_THRESHOLDS = {
    'PUBLIC': 0.0,      # Always accessible
    'PRIVILEGED': 0.55, # Requires almost perfect static (92% of max base trust)
    'EXCLUSIVE': 0.8    # Requires base + earned trust (dynamic)
}

def get_trust_threshold(layer: NuggetLayer) -> float:
    """Get the trust threshold required for a nugget layer"""
    threshold_map = {
        NuggetLayer.PUBLIC: NUGGET_THRESHOLDS['PUBLIC'],
        NuggetLayer.PRIVILEGED: NUGGET_THRESHOLDS['PRIVILEGED'],
        NuggetLayer.EXCLUSIVE: NUGGET_THRESHOLDS['EXCLUSIVE']
    }
    return threshold_map[layer]

def can_access_nugget(trust_level: float, layer: NuggetLayer) -> bool:
    """Check if a trust level can access a nugget layer"""
    return trust_level >= get_trust_threshold(layer)

class TrustNugget(BaseModel):
    id: int
    title: str
    character_ids: List[int]
    level_1_content: str  # Public level content (always required)
    level_2_content: Optional[str] = None  # Privileged level content (optional)
    level_3_content: Optional[str] = None  # Exclusive level content (optional)

class TrustNuggetCreate(BaseModel):
    title: str
    character_ids: List[int]
    level_1_content: str
    level_2_content: Optional[str] = None
    level_3_content: Optional[str] = None
