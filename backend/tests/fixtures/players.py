from app.models.player import PlayerCreate
from app.models.race import Race, Size, Gender
from app.models.alignment import Alignment
from app.models.class_traits import Abilities, Class, Skills

players_db = [
    PlayerCreate(
        user_id=1,
        world_id=1,
        name="Silviana Moonleaf",
        appearance="Graceful elf with silver hair braided with leaves, violet eyes, and elegant elven robes",
        race=Race.HIGH_ELF.value,
        class_name=Class.WIZARD.value,
        size=Size.MEDIUM.value,
        alignment=Alignment.NEUTRAL_GOOD.value,
        gender=Gender.FEMALE.value,
        abilities={
            Abilities.CHARISMA.value: 15
        },
        skills={
            Skills.PERSUASION.value: 5,
            Skills.DECEPTION.value: 2,
            Skills.INTIMIDATION.value: 3,
            Skills.PERFORMANCE.value: 4
        }
    ),
    PlayerCreate(
        user_id=1,
        world_id=1,
        name="Pippin Greenhill",
        appearance="Cheerful hobbit with curly auburn hair, bright brown eyes, and well-worn traveling clothes",
        race=Race.LIGHTFOOT_HALFLING.value,
        class_name=Class.BARD.value,
        size=Size.SMALL.value,
        alignment=Alignment.CHAOTIC_GOOD.value,
        gender=Gender.MALE.value,
        abilities={
            Abilities.CHARISMA.value: 17
        },
        skills={
            Skills.PERSUASION.value: 7,
            Skills.DECEPTION.value: 3,
            Skills.INTIMIDATION.value: 2,
            Skills.PERFORMANCE.value: 6
        }
    ),
]
