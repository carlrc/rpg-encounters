from typing import Optional, List
from app.models.character import Character, CharacterCreate, CharacterUpdate
from tests.fixtures.characters import characters_db, next_character_id


class CharacterStore:
    def __init__(self):
        self.characters = characters_db
        self.next_id = next_character_id

    def get_all_characters(self) -> List[Character]:
        """Get all characters"""
        return list(self.characters.values())

    def get_character_by_id(self, character_id: int) -> Optional[Character]:
        """Get a specific character by ID"""
        return self.characters.get(character_id)

    def create_character(self, character_data: CharacterCreate) -> Character:
        """Create a new character"""
        character_dict = character_data.model_dump()
        character_dict["id"] = self.next_id

        new_character = Character(**character_dict)
        self.characters[self.next_id] = new_character
        self.next_id += 1

        return new_character

    def update_character(
        self, character_id: int, character_update: CharacterUpdate
    ) -> Optional[Character]:
        """Update an existing character"""
        if character_id not in self.characters:
            return None

        existing_character = self.characters[character_id]
        update_data = character_update.model_dump(exclude_unset=True)

        # Update the existing character with new data
        updated_data = existing_character.model_dump()
        updated_data.update(update_data)

        updated_character = Character(**updated_data)
        self.characters[character_id] = updated_character

        return updated_character

    def delete_character(self, character_id: int) -> bool:
        """Delete a character"""
        if character_id not in self.characters:
            return False

        del self.characters[character_id]
        return True

    def character_exists(self, character_id: int) -> bool:
        """Check if a character exists"""
        return character_id in self.characters


# Create a singleton instance
character_store = CharacterStore()
