from typing import Optional, List
from app.models.character import Character, CharacterCreate, CharacterUpdate, CharacterRace, CharacterSize, CharacterAlignment

characters_db = {
    1: Character(
        id=1,
        name="Bingo Bracegirdle",
        avatar=None,
        race=CharacterRace.HALFLING.value,
        size=CharacterSize.SMALL.value,
        alignment=CharacterAlignment.NEUTRAL_GOOD.value,
        profession="Barkeep",
        background="Friendly tavern keeper who runs the village inn. Knows everyone in town and all the local gossip. Makes excellent ale and hearty meals for weary travelers.",
        communication_style="Chatty and welcoming, always ready with a story or bit of news. Speaks warmly and uses folksy expressions. Loves to make guests feel at home.",
        motivation="To keep the tavern running smoothly and to pay the bills."
    ),
    2: Character(
        id=2,
        name="Old Took",
        avatar=None,
        race=CharacterRace.HALFLING.value,
        size=CharacterSize.SMALL.value,
        alignment=CharacterAlignment.CHAOTIC_GOOD.value,
        profession="Retiree",
        background="Former village elder who has seen many seasons come and go. Full of stories about the old days and local history. Enjoys his pipe and afternoon tea.",
        communication_style="Rambling and storytelling, often goes off on tangents about the past. Wise but scattered, loves sharing tales and memories with anyone who will listen.",
        motivation="To tell stories of the old days."
    ),
    3: Character(
        id=3,
        name="Poppy Proudfoot",
        avatar=None,
        race=CharacterRace.HALFLING.value,
        size=CharacterSize.SMALL.value,
        alignment=CharacterAlignment.LAWFUL_GOOD.value,
        profession="Baker",
        background="Village baker who creates the most delicious pies, breads, and pastries. Her kitchen always smells wonderful and neighbors often stop by for fresh baked goods.",
        communication_style="Warm and motherly, speaks with care and concern for others. Often offers food as comfort and uses baking metaphors in conversation.",
        motivation="To bring people joy with food, but also to pay the bills."
    ),
    4: Character(
        id=4,
        name="Merry Greenhill",
        avatar=None,
        race=CharacterRace.HALFLING.value,
        size=CharacterSize.SMALL.value,
        alignment=CharacterAlignment.NEUTRAL_EVIL.value,
        profession="Gardener",
        background="Village gardener who maintains the community gardens and helps neighbors with their vegetable patches. Known for growing the finest pipe-weed in the area.",
        communication_style="Down-to-earth and practical.",
        motivation="Become the best gardener. Even if it means destroying others that he is jealous of."
    )
}
next_character_id = 5

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

    def update_character(self, character_id: int, character_update: CharacterUpdate) -> Optional[Character]:
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
