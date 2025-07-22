from typing import Optional, Dict
from app.models.trust import TrustState


class TrustStateStore:
    def __init__(self):
        self.trust_states: Dict[tuple, TrustState] = (
            {}
        )  # (character_id, player_id) -> TrustState

    def get_or_create(
        self, character_id: int, player_id: int, base_trust: float = 0.0
    ) -> TrustState:
        """Get existing trust state or create new one"""
        key = (character_id, player_id)
        if key not in self.trust_states:
            self.trust_states[key] = TrustState(
                character_id=character_id,
                player_id=player_id,
                base_trust=base_trust,
                earned_trust=0.0,
            )
        return self.trust_states[key]

    def update_trust_state(self, trust_state: TrustState) -> TrustState:
        """Update an existing trust state"""
        key = (trust_state.character_id, trust_state.player_id)
        self.trust_states[key] = trust_state
        return trust_state

    def get_trust_state(
        self, character_id: int, player_id: int
    ) -> Optional[TrustState]:
        """Get trust state for character-player pair"""
        key = (character_id, player_id)
        return self.trust_states.get(key)

    def reset_trust_state(self, character_id: int, player_id: int) -> bool:
        """Reset earned trust to 0.0, keep base trust"""
        key = (character_id, player_id)
        if key in self.trust_states:
            self.trust_states[key].earned_trust = 0.0
            return True
        return False

    def clear(self) -> None:
        """Clear all trust states - used for testing"""
        self.trust_states.clear()


# Create singleton instance
trust_state_store = TrustStateStore()
