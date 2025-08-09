from typing import Optional, List
from app.models.nugget import Truth, TruthCreate
from tests.fixtures.nuggets import truth_db, next_truth_id


class TruthStore:
    def __init__(self):
        self.truths = truth_db
        self.next_id = next_truth_id

    def get_all_truths(self) -> List[Truth]:
        """Get all truths across all characters"""
        return list(self.truths.values())

    def get_by_character_id(self, character_id: int) -> List[Truth]:
        """Get all truths for a character"""
        return [
            truth
            for truth in self.truths.values()
            if character_id in truth.character_ids
        ]

    def get_truth(self, truth_id: int) -> Optional[Truth]:
        """Get a specific truth by ID"""
        return self.truths.get(truth_id)

    def get_by_id(self, truth_id: int) -> Optional[Truth]:
        """Get a specific truth by ID (alias for get_truth)"""
        return self.truths.get(truth_id)

    def create_truth(self, truth_data: TruthCreate) -> Truth:
        """Create a new truth"""
        truth_dict = truth_data.model_dump()
        truth_dict["id"] = self.next_id

        truth = Truth(**truth_dict)
        self.truths[self.next_id] = truth
        self.next_id += 1

        return truth

    def update_truth(self, truth_id: int, updates: dict) -> Optional[Truth]:
        """Update an existing truth"""
        if truth_id not in self.truths:
            return None

        existing_truth = self.truths[truth_id]
        update_data = existing_truth.model_dump()
        update_data.update(updates)

        updated_truth = Truth(**update_data)
        self.truths[truth_id] = updated_truth
        return updated_truth

    def delete_truth(self, truth_id: int) -> bool:
        """Delete a truth"""
        if truth_id not in self.truths:
            return False
        del self.truths[truth_id]
        return True


# Create singleton instance
truth_store = TruthStore()
