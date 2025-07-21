from typing import Optional, List
from app.models.nugget import TrustNugget, TrustNuggetCreate
from tests.fixtures.nuggets import nugget_db, next_nugget_id

class NuggetStore:
    def __init__(self):
        self.nuggets = nugget_db
        self.next_id = next_nugget_id

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

# Create singleton instance
nugget_store = NuggetStore()
