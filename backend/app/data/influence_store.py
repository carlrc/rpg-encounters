from typing import Dict

from app.models.influence import Influence


class InfluenceStore:
    def __init__(self):
        self.influence_states: Dict[tuple, Influence] = (
            {}
        )  # (character_id, player_id) -> Influence

    def get_or_create(
        self, character_id: int, player_id: int, base: float = 0.0
    ) -> Influence:
        """Get existing influence state or create new one"""
        key = (character_id, player_id)
        if key not in self.influence_states:
            self.influence_states[key] = Influence(
                character_id=character_id,
                player_id=player_id,
                base=base,
                earned=0.0,
            )
        return self.influence_states[key]

    def update_influence(self, influence: Influence) -> Influence:
        """Update an existing influence state"""
        key = (influence.character_id, influence.player_id)
        self.influence_states[key] = influence
        return influence

    def get_influence(self, character_id: int, player_id: int) -> Influence | None:
        """Get influence state for character-player pair"""
        key = (character_id, player_id)
        return self.influence_states.get(key)

    def reset_influence(self, character_id: int, player_id: int) -> bool:
        """Reset earned influence to 0.0, keep base influence"""
        key = (character_id, player_id)
        if key in self.influence_states:
            self.influence_states[key].earned = 0.0
            return True
        return False

    def clear(self) -> None:
        """Clear all influence states - used for testing"""
        self.influence_states.clear()


# Global instance for backward compatibility during transition
influence_store = InfluenceStore()
