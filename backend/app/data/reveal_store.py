from typing import List

from app.models.reveal import Reveal, RevealCreate
from tests.fixtures.reveals import next_reveal_id, reveal_db


class RevealStore:
    def __init__(self):
        self.reveals = reveal_db
        self.next_id = next_reveal_id

    def get_all_reveals(self) -> List[Reveal]:
        """Get all reveals across all characters"""
        return list(self.reveals.values())

    def get_by_character_id(self, character_id: int) -> List[Reveal]:
        """Get all reveals for a character"""
        return [
            reveal
            for reveal in self.reveals.values()
            if character_id in reveal.character_ids
        ]

    def get_reveal(self, reveal_id: int) -> Reveal | None:
        """Get a specific reveal by ID"""
        return self.reveals.get(reveal_id)

    def get_by_id(self, reveal_id: int) -> Reveal | None:
        """Get a specific reveal by ID (alias for get_reveal)"""
        return self.reveals.get(reveal_id)

    def create_reveal(self, reveal_data: RevealCreate) -> Reveal:
        """Create a new reveal"""
        reveal_dict = reveal_data.model_dump()
        reveal_dict["id"] = self.next_id

        reveal = Reveal(**reveal_dict)
        self.reveals[self.next_id] = reveal
        self.next_id += 1

        return reveal

    def update_reveal(self, reveal_id: int, updates: dict) -> Reveal | None:
        """Update an existing reveal"""
        if reveal_id not in self.reveals:
            return None

        existing_reveal = self.reveals[reveal_id]
        update_data = existing_reveal.model_dump()
        update_data.update(updates)

        updated_reveal = Reveal(**update_data)
        self.reveals[reveal_id] = updated_reveal
        return updated_reveal

    def delete_reveal(self, reveal_id: int) -> bool:
        """Delete a reveal"""
        if reveal_id not in self.reveals:
            return False
        del self.reveals[reveal_id]
        return True
