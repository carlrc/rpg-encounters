from typing import List
from app.models.nugget import NuggetLayer, NUGGET_THRESHOLDS, TrustNugget


class NuggetService:
    @staticmethod
    def get_trust_threshold(layer: NuggetLayer) -> float:
        """Get the trust threshold required for a nugget layer"""
        threshold_map = {
            NuggetLayer.PUBLIC: NUGGET_THRESHOLDS['PUBLIC'],
            NuggetLayer.PRIVILEGED: NUGGET_THRESHOLDS['PRIVILEGED'],
            NuggetLayer.EXCLUSIVE: NUGGET_THRESHOLDS['EXCLUSIVE']
        }
        return threshold_map[layer]

    @staticmethod
    def can_access_nugget(trust_level: float, layer: NuggetLayer) -> bool:
        """Check if a trust level can access a nugget layer"""
        return trust_level >= NuggetService.get_trust_threshold(layer)

    @staticmethod
    def categorize_nuggets_by_trust(trust_state, all_nuggets: List[TrustNugget]) -> tuple[List[str], List[str]]:
        """
        Categorize nuggets into available and unavailable based on trust level.
        Returns tuple of (available_nuggets, unavailable_nuggets)
        """
        available_nuggets = []
        unavailable_nuggets = []
        
        for nugget in all_nuggets:
            # Check each level of content and add to appropriate list
            if nugget.level_1_content:
                if trust_state.total_trust >= NuggetService.get_trust_threshold(NuggetLayer.PUBLIC):
                    available_nuggets.append(nugget.level_1_content)
                else:
                    unavailable_nuggets.append(nugget.level_1_content)
            
            if nugget.level_2_content:
                if trust_state.total_trust >= NuggetService.get_trust_threshold(NuggetLayer.PRIVILEGED):
                    available_nuggets.append(nugget.level_2_content)
                else:
                    unavailable_nuggets.append(nugget.level_2_content)
            
            if nugget.level_3_content:
                if trust_state.total_trust >= NuggetService.get_trust_threshold(NuggetLayer.EXCLUSIVE):
                    available_nuggets.append(nugget.level_3_content)
                else:
                    unavailable_nuggets.append(nugget.level_3_content)
        
        return available_nuggets, unavailable_nuggets
