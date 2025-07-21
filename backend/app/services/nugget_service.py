from typing import List
from app.models.nugget import NuggetLayer, NUGGET_THRESHOLDS, TrustNugget, NuggetLevelInfo
from app.models.trust import TrustState


class NuggetService:
    @staticmethod
    def get_trust_threshold(layer: NuggetLayer) -> float:
        """Get the trust threshold required for a nugget layer"""
        threshold_map = {
            NuggetLayer.PUBLIC: NUGGET_THRESHOLDS[NuggetLayer.PUBLIC.name],
            NuggetLayer.PRIVILEGED: NUGGET_THRESHOLDS[NuggetLayer.PRIVILEGED.name],
            NuggetLayer.EXCLUSIVE: NUGGET_THRESHOLDS[NuggetLayer.EXCLUSIVE.name]
        }
        return threshold_map[layer]

    @staticmethod
    def can_access_nugget(trust_level: float, layer: NuggetLayer) -> bool:
        """Check if a trust level can access a nugget layer"""
        return trust_level >= NuggetService.get_trust_threshold(layer)

    @staticmethod
    def categorize_nuggets_by_trust(trust_state: TrustState, all_nuggets: List[TrustNugget]) -> List[NuggetLevelInfo]:
        """
        Categorize nuggets by trust level, returning structured information about each level.
        Returns list of NuggetLevelInfo objects with content, level, and availability.
        """
        nugget_levels = []
        for nugget in all_nuggets:
            # Check each level of content and create NuggetLevelInfo objects
            if nugget.level_1_content:
                available = trust_state.total_trust >= NuggetService.get_trust_threshold(NuggetLayer.PUBLIC)
                nugget_levels.append(NuggetLevelInfo(
                    content=nugget.level_1_content,
                    level=NuggetLayer.PUBLIC.name,
                    available=available
                ))
            
            if nugget.level_2_content:
                available = trust_state.total_trust >= NuggetService.get_trust_threshold(NuggetLayer.PRIVILEGED)
                nugget_levels.append(NuggetLevelInfo(
                    content=nugget.level_2_content,
                    level=NuggetLayer.PRIVILEGED.name,
                    available=available
                ))
            
            if nugget.level_3_content:
                available = trust_state.total_trust >= NuggetService.get_trust_threshold(NuggetLayer.EXCLUSIVE)
                nugget_levels.append(NuggetLevelInfo(
                    content=nugget.level_3_content,
                    level=NuggetLayer.EXCLUSIVE.name,
                    available=available
                ))
        
        return nugget_levels
