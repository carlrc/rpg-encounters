from app.models.trust import TrustProfile, BASE_TRUST_MIN, BASE_TRUST_MAX, PREFERENCE_VALUE_MAX
from app.models.player import Player

class TrustCalculator:
    @staticmethod
    def calculate_base_trust(trust_profile: TrustProfile, player: Player) -> float:
        """Calculate starting trust from player characteristics (±0.3 each)"""
        trust = 0.0
        
        # Race preference
        trust += trust_profile.race_preferences.get(player.race, 0.0)
        
        # Class preference  
        trust += trust_profile.class_preferences.get(player.class_name, 0.0)
        
        # Gender preference
        trust += trust_profile.gender_preferences.get(player.gender, 0.0)
        
        # Size preference
        trust += trust_profile.size_preferences.get(player.size, 0.0)
        
        # Appearance keywords (±0.3 if any keyword matches)
        if any(keyword.lower() in player.appearance.lower() 
               for keyword in trust_profile.appearance_keywords):
            trust += PREFERENCE_VALUE_MAX
            
        return max(BASE_TRUST_MIN, min(BASE_TRUST_MAX, trust))
