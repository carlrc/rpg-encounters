from app.models.player import PlayerCreate
from app.models.race import Race, Size, Gender
from app.models.alignment import Alignment
from app.models.class_traits import Abilities, Class, Skills

players_db = [
    PlayerCreate(
        user_id=1,
        world_id=1,
        name="Mira Underbough",
        rl_name="Sarah Johnson",
        appearance="Small lightfoot halfling with quick hands and a guarded smile.",
        race=Race.LIGHTFOOT_HALFLING.value,
        class_name=Class.ROGUE.value,
        size=Size.SMALL.value,
        alignment=Alignment.CHAOTIC_GOOD.value,
        gender=Gender.FEMALE.value,
        abilities={
            Abilities.CHARISMA.value: 3
        },
        skills={
            Skills.DECEPTION.value: 5,
            Skills.INTIMIDATION.value: 3,
            Skills.PERFORMANCE.value: 3,
            Skills.PERSUASION.value: 3
        }
    ),
    PlayerCreate(
        user_id=1,
        world_id=1,
        name="Sir Alaric Duskbane",
        rl_name="Michael Chen",
        appearance="Human paladin in chain mail with noble bearing and a resolute gaze.",
        race=Race.HUMAN.value,
        class_name=Class.PALADIN.value,
        size=Size.MEDIUM.value,
        alignment=Alignment.LAWFUL_GOOD.value,
        gender=Gender.MALE.value,
        abilities={
            Abilities.CHARISMA.value: 2
        },
        skills={
            Skills.DECEPTION.value: 2,
            Skills.INTIMIDATION.value: 4,
            Skills.PERFORMANCE.value: 2,
            Skills.PERSUASION.value: 4
        }
    ),
    PlayerCreate(
        user_id=1,
        world_id=1,
        name="Thalion Oakenshade",
        rl_name="David Williams",
        appearance="Wood elf fighter with lean build, carrying a greatsword and longbow.",
        race=Race.WOOD_ELF.value,
        class_name=Class.FIGHTER.value,
        size=Size.MEDIUM.value,
        alignment=Alignment.NEUTRAL_GOOD.value,
        gender=Gender.MALE.value,
        abilities={
            Abilities.CHARISMA.value: -1
        },
        skills={
            Skills.DECEPTION.value: -1,
            Skills.INTIMIDATION.value: -1,
            Skills.PERFORMANCE.value: -1,
            Skills.PERSUASION.value: -1
        }
    ),
    PlayerCreate(
        user_id=1,
        world_id=1,
        name="Brynja Stoneforge",
        rl_name="Emma Rodriguez",
        appearance="Hill dwarf cleric in chain mail with a sturdy build and a bright holy symbol.",
        race=Race.HILL_DWARF.value,
        class_name=Class.CLERIC.value,
        size=Size.MEDIUM.value,
        alignment=Alignment.LAWFUL_GOOD.value,
        gender=Gender.FEMALE.value,
        abilities={
            Abilities.CHARISMA.value: 0
        },
        skills={
            Skills.DECEPTION.value: 1,
            Skills.INTIMIDATION.value: 3,
            Skills.PERFORMANCE.value: 1,
            Skills.PERSUASION.value: 1
        }
    ),
    PlayerCreate(
        user_id=1,
        world_id=1,
        name="Elaris Moonglade",
        rl_name="James Thompson",
        appearance="High elf wizard with scholarly robes and a curious, observant demeanor.",
        race=Race.HIGH_ELF.value,
        class_name=Class.WIZARD.value,
        size=Size.MEDIUM.value,
        alignment=Alignment.NEUTRAL_GOOD.value,
        gender=Gender.MALE.value,
        abilities={
            Abilities.CHARISMA.value: 1
        },
        skills={
            Skills.DECEPTION.value: -1,
            Skills.INTIMIDATION.value: -1,
            Skills.PERFORMANCE.value: -1,
            Skills.PERSUASION.value: -1
        }
    )
]
