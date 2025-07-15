from typing import Optional, List
from app.models.character import Character, CharacterCreate, CharacterUpdate, CharacterRace, CharacterSize, CharacterAlignment

characters_db = {
    1: Character(
        id=1,
        name="Elara Moonwhisper",
        avatar=None,
        race=CharacterRace.ELF.value,
        size=CharacterSize.MEDIUM.value,
        alignment=CharacterAlignment.NEUTRAL_GOOD.value,
        profession="Merchant",
        background="A traveling merchant who has seen many lands and peoples. She values knowledge and fair trade above all else. Her family runs a network of trading posts across the realm.",
        communication_style="Speaks softly with measured words, often pausing to consider responses carefully.",
        tags=["#merchant", "#traveler", "#knowledge-seeker"]
    ),
    2: Character(
        id=2,
        name="Thorin Ironforge",
        avatar=None,
        race=CharacterRace.DWARF.value,
        size=CharacterSize.MEDIUM.value,
        alignment=CharacterAlignment.LAWFUL_GOOD.value,
        profession="Guard",
        background="A veteran city guard who has protected the gates for over twenty years. Known for his unwavering sense of duty and his ability to spot trouble from a mile away.",
        communication_style="Direct and gruff, but fair. Uses few words but makes them count.",
        tags=["#guard", "#veteran", "#duty-bound"]
    ),
    3: Character(
        id=3,
        name="Zara the Wise",
        avatar=None,
        race=CharacterRace.HUMAN.value,
        size=CharacterSize.MEDIUM.value,
        alignment=CharacterAlignment.TRUE_NEUTRAL.value,
        profession="Mage",
        background="An accomplished wizard who runs the local magic academy. She has dedicated her life to the study of arcane arts and teaching the next generation of spellcasters.",
        communication_style="Scholarly and precise, often references ancient texts and magical theory.",
        tags=["#mage", "#teacher", "#scholar"]
    ),
    4: Character(
        id=4,
        name="Lord Aldric Blackwood",
        avatar=None,
        race=CharacterRace.HUMAN.value,
        size=CharacterSize.MEDIUM.value,
        alignment=CharacterAlignment.LAWFUL_NEUTRAL.value,
        profession="Noble",
        background="A minor lord who oversees a small but prosperous region. He is known for his political acumen and his ability to navigate court intrigue with skill.",
        communication_style="Formal and diplomatic, chooses words carefully to avoid offense.",
        tags=["#noble", "#politician", "#courtly"]
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
