from app.models.trust import TrustProfile

trust_profiles_db = {
    1: TrustProfile(
        character_id=1,
        race_preferences={
            "Human": 0.2,
            "Dwarf": -0.1,
            "Elf": 0.1
        },
        class_preferences={
            "Fighter": 0.1,
            "Rogue": -0.2
        },
        gender_preferences={
            "nonbinary": 0.0
        },
        size_preferences={
            "Medium": 0.0
        },
        appearance_keywords=[],
        storytelling_keywords=[]
    ),
    2: TrustProfile(
        character_id=2,
        race_preferences={
            "Halfling": 0.3,
            "Human": 0.1,
            "Orc": -0.3
        },
        class_preferences={
            "Bard": 0.2,
            "Wizard": 0.1,
            "Barbarian": -0.2
        },
        gender_preferences={
            "male": 0.1
        },
        size_preferences={
            "Small": 0.2
        },
        appearance_keywords=[],
        storytelling_keywords=[]
    ),
    3: TrustProfile(
        character_id=3,
        race_preferences={
            "Halfling": 0.2,
            "Human": 0.1,
            "Tiefling": -0.1
        },
        class_preferences={
            "Cleric": 0.3,
            "Paladin": 0.2,
            "Warlock": -0.3
        },
        gender_preferences={
            "female": 0.1,
            "nonbinary": 0.0
        },
        size_preferences={
            "Small": 0.1,
            "Medium": 0.0
        },
        appearance_keywords=[],
        storytelling_keywords=[]
    ),
    4: TrustProfile(
        character_id=4,
        race_preferences={
            "Halfling": 0.1,
            "Elf": -0.2,
            "Dwarf": -0.1
        },
        class_preferences={
            "Druid": 0.3,
            "Ranger": 0.2,
            "Sorcerer": -0.1
        },
        gender_preferences={
            "male": 0.0
        },
        size_preferences={
            "Small": 0.2,
            "Large": -0.1
        },
        appearance_keywords=[],
        storytelling_keywords=[]
    )
}
