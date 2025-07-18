from typing import Optional, List, Dict
from app.models.trust import TrustProfile, TrustProfileCreate, TrustNugget, TrustNuggetCreate, TrustState, TrustStateCreate, NuggetLayer

class TrustProfileStore:
    def __init__(self):
        self.trust_profiles: Dict[int, TrustProfile] = {}  # character_id -> TrustProfile

    def get_by_character_id(self, character_id: int) -> Optional[TrustProfile]:
        """Get trust profile for a character"""
        return self.trust_profiles.get(character_id)

    def create_trust_profile(self, profile_data: TrustProfileCreate) -> TrustProfile:
        """Create a new trust profile"""
        profile = TrustProfile(**profile_data.model_dump())
        self.trust_profiles[profile.character_id] = profile
        return profile

    def update_trust_profile(self, character_id: int, updates: dict) -> Optional[TrustProfile]:
        """Update an existing trust profile"""
        if character_id not in self.trust_profiles:
            return None
        
        existing_profile = self.trust_profiles[character_id]
        update_data = existing_profile.model_dump()
        update_data.update(updates)
        
        updated_profile = TrustProfile(**update_data)
        self.trust_profiles[character_id] = updated_profile
        return updated_profile

    def delete_trust_profile(self, character_id: int) -> bool:
        """Delete a trust profile"""
        if character_id not in self.trust_profiles:
            return False
        del self.trust_profiles[character_id]
        return True


class NuggetStore:
    def __init__(self):
        self.nuggets: Dict[int, TrustNugget] = {}  # nugget_id -> TrustNugget
        self.next_id = 1

    def get_all_nuggets(self) -> List[TrustNugget]:
        """Get all nuggets across all characters"""
        return list(self.nuggets.values())

    def get_by_character_id(self, character_id: int) -> List[TrustNugget]:
        """Get all nuggets for a character"""
        return [nugget for nugget in self.nuggets.values() if character_id in nugget.character_ids]

    def get_nugget(self, nugget_id: int) -> Optional[TrustNugget]:
        """Get a specific nugget by ID"""
        return self.nuggets.get(nugget_id)

    def get_by_id(self, nugget_id: int) -> Optional[TrustNugget]:
        """Get a specific nugget by ID (alias for get_nugget)"""
        return self.nuggets.get(nugget_id)

    def create_nugget(self, nugget_data: TrustNuggetCreate) -> TrustNugget:
        """Create a new nugget"""
        nugget_dict = nugget_data.model_dump()
        nugget_dict["id"] = self.next_id
        
        nugget = TrustNugget(**nugget_dict)
        self.nuggets[self.next_id] = nugget
        self.next_id += 1
        
        return nugget

    def update_nugget(self, nugget_id: int, updates: dict) -> Optional[TrustNugget]:
        """Update an existing nugget"""
        if nugget_id not in self.nuggets:
            return None
        
        existing_nugget = self.nuggets[nugget_id]
        update_data = existing_nugget.model_dump()
        update_data.update(updates)
        
        updated_nugget = TrustNugget(**update_data)
        self.nuggets[nugget_id] = updated_nugget
        return updated_nugget

    def delete_nugget(self, nugget_id: int) -> bool:
        """Delete a nugget"""
        if nugget_id not in self.nuggets:
            return False
        del self.nuggets[nugget_id]
        return True


class TrustStateStore:
    def __init__(self):
        self.trust_states: Dict[tuple, TrustState] = {}  # (character_id, player_id) -> TrustState

    def get_or_create(self, character_id: int, player_id: int, base_trust: float = 0.0) -> TrustState:
        """Get existing trust state or create new one"""
        key = (character_id, player_id)
        if key not in self.trust_states:
            self.trust_states[key] = TrustState(
                character_id=character_id,
                player_id=player_id,
                base_trust=base_trust,
                earned_trust=0.0
            )
        return self.trust_states[key]

    def update_trust_state(self, trust_state: TrustState) -> TrustState:
        """Update an existing trust state"""
        key = (trust_state.character_id, trust_state.player_id)
        self.trust_states[key] = trust_state
        return trust_state

    def get_trust_state(self, character_id: int, player_id: int) -> Optional[TrustState]:
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


# Create singleton instances
trust_profile_store = TrustProfileStore()
nugget_store = NuggetStore()
trust_state_store = TrustStateStore()

# Load trust profiles from fixtures
from tests.fixtures.trust import trust_profiles_db
trust_profile_store.trust_profiles = trust_profiles_db
