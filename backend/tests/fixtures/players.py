from app.models.player import Abilities, Player, PlayerClass, Skills
from app.models.race import Race, Size, Gender
from app.models.alignment import Alignment

players_db = {
    1: Player(
        id=1,
        name="Silviana Moonleaf",
        appearance="Graceful elf with silver hair braided with leaves, violet eyes, and elegant elven robes",
        race=Race.HIGH_ELF.value,
        class_name=PlayerClass.WIZARD.value,
        size=Size.MEDIUM.value,
        alignment=Alignment.NEUTRAL_GOOD.value,
        gender=Gender.FEMALE.value,
        abilities={
            Abilities.CHARISMA: +1
        },
        skills={
            Skills.PERSUASION: +1
        }
    ),
    2: Player(
        id=2,
        name="Pippin Greenhill",
        appearance="Cheerful hobbit with curly auburn hair, bright brown eyes, and well-worn traveling clothes",
        race=Race.LIGHTFOOT_HALFLING.value,
        class_name=PlayerClass.BARD.value,
        size=Size.SMALL.value,
        alignment=Alignment.CHAOTIC_GOOD.value,
        gender=Gender.MALE.value,
        abilities={
            Abilities.CHARISMA: +1
        },
        skills={
            Skills.PERSUASION: +1
        }
    ),
}

next_player_id = 3
