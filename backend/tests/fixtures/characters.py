from app.models.character import Character, CharacterRace, CharacterSize, CharacterAlignment

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
        motivation="To keep the tavern running smoothly and to pay the bills.",
        voice="MFZUKuGQUsGJPQjTS4wC",
        race_preferences={"Halfling": 0.3},
        appearance_keywords=None,
        storytelling_keywords=None
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
        motivation="To tell stories of the old days.",
        voice="j9jfwdrw7BRfcR43Qohk",
        race_preferences={"Halfling": 0.3, "Human": 0.1, "Orc": -0.3},
        class_preferences={"Bard": 0.2, "Wizard": 0.1, "Barbarian": -0.2},
        gender_preferences={"male": 0.1},
        size_preferences={"Small": 0.2},
        appearance_keywords=[],
        storytelling_keywords=[]
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
        motivation="To bring people joy with food, but also to pay the bills.",
        voice="ZF6FPAbjXT4488VcRRnw",
        race_preferences={"Halfling": 0.2, "Human": 0.1, "Tiefling": -0.1},
        class_preferences={"Cleric": 0.3, "Paladin": 0.2, "Warlock": -0.3},
        gender_preferences={"female": 0.1, "nonbinary": 0.0},
        size_preferences={"Small": 0.1, "Medium": 0.0},
        appearance_keywords=[],
        storytelling_keywords=[]
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
        motivation="Become the best gardener. Even if it means destroying others that he is jealous of.",
        voice="6OzrBCQf8cjERkYgzSg8",
        race_preferences={"Halfling": 0.1, "Elf": -0.2, "Dwarf": -0.1},
        class_preferences={"Druid": 0.3, "Ranger": 0.2, "Sorcerer": -0.1},
        gender_preferences={"male": 0.0},
        size_preferences={"Small": 0.2, "Large": -0.1},
        appearance_keywords=[],
        storytelling_keywords=[]
    )
}

next_character_id = 5
