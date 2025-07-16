from typing import Optional, List
from app.models.character import Character, CharacterCreate, CharacterUpdate, CharacterRace, CharacterSize, CharacterAlignment

characters_db = {
    1: Character(
        id=1,
        name="Elrond",
        avatar=None,
        race=CharacterRace.ELF.value,
        size=CharacterSize.MEDIUM.value,
        alignment=CharacterAlignment.LAWFUL_GOOD.value,
        profession="Lord of Rivendell",
        background="Ancient Elf-lord who has witnessed the rise and fall of kingdoms. Master of lore and healing, keeper of Vilya, one of the three Elven rings of power.",
        communication_style="Speaks with ancient wisdom and gravitas, often referencing historical events. Measured and thoughtful in all responses.",
        motivation="To defeat evil and protect the elves."
    ),
    2: Character(
        id=2,
        name="Boromir",
        avatar=None,
        race=CharacterRace.HUMAN.value,
        size=CharacterSize.MEDIUM.value,
        alignment=CharacterAlignment.LAWFUL_GOOD.value,
        profession="Captain of Gondor",
        background="Son of Denethor, Steward of Gondor. A warrior who has defended Minas Tirith against the forces of Mordor. Proud of his city and people.",
        communication_style="Direct and passionate, speaks with the authority of Gondor. Can be forceful when discussing threats to his homeland.",
        motivation="To protect Gondor."
    ),
    3: Character(
        id=3,
        name="Galadriel",
        avatar=None,
        race=CharacterRace.ELF.value,
        size=CharacterSize.MEDIUM.value,
        alignment=CharacterAlignment.NEUTRAL_GOOD.value,
        profession="Lady of Lothlórien",
        background="One of the mightiest Elves in Middle-earth, keeper of Nenya, the Ring of Water. Possesses the gift of foresight and great wisdom.",
        communication_style="Speaks with ethereal grace and mysterious depth. Speaks in riddles or prophecy.",
        motivation="Power but not at all cost"
    ),
    4: Character(
        id=4,
        name="Théoden",
        avatar=None,
        race=CharacterRace.HUMAN.value,
        size=CharacterSize.MEDIUM.value,
        alignment=CharacterAlignment.LAWFUL_GOOD.value,
        profession="King of Rohan",
        background="King of the Rohirrim, master of horses and the great hall of Edoras. Recently freed from Saruman's influence, he has regained his strength and resolve.",
        communication_style="Speaks with kingly authority and the wisdom of age. References the glory of Rohan and the deeds of his ancestors.",
        motivation="To lead his people with honor and defend Rohan."
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
