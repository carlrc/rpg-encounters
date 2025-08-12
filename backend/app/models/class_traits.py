from enum import Enum


class Class(Enum):
    BARBARIAN = "Barbarian"
    BARD = "Bard"
    CLERIC = "Cleric"
    DRUID = "Druid"
    FIGHTER = "Fighter"
    MONK = "Monk"
    PALADIN = "Paladin"
    RANGER = "Ranger"
    ROGUE = "Rogue"
    SORCERER = "Sorcerer"
    WARLOCK = "Warlock"
    WIZARD = "Wizard"


class Abilities(Enum):
    CHARISMA = "Charisma"


class Skills(Enum):
    DECEPTION = "Deception"
    INTIMIDATION = "Intimidation"
    PERFORMANCE = "Performance"
    PERSUASION = "Persuasion"


VALID_CLASSES = [class_name.value for class_name in Class]
VALID_ABILITIES = [ability.value for ability in Abilities]
VALID_SKILLS = [skill.value for skill in Skills]
ABILITY_SCORE_MIN = 0
ABILITY_SCORE_MAX = 30
SKILL_SCORE_MIN = -5
SKILL_SCORE_MAX = 25
