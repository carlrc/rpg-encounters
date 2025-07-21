from app.models.character import Character
from app.models.player import Player
from app.models.trust import BASE_TRUST_MIN, BASE_TRUST_MAX

class TrustCalculator:
    @staticmethod
    def calculate_base_trust(character: Character, player: Player) -> float:
        """Calculate starting trust from player characteristics (±0.3 each)"""
        trust = 0.0
        
        # Race preference
        if character.race_preferences:
            trust += character.race_preferences.get(player.race, 0.0)
        
        # Class preference  
        if character.class_preferences:
            trust += character.class_preferences.get(player.class_name, 0.0)
        
        # Gender preference
        if character.gender_preferences:
            trust += character.gender_preferences.get(player.gender, 0.0)
        
        # Size preference
        if character.size_preferences:
            trust += character.size_preferences.get(player.size, 0.0)
            
        return max(BASE_TRUST_MIN, min(BASE_TRUST_MAX, trust))
