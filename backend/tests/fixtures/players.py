from app.models.player import Player, PlayerClass
from app.models.character import CharacterRace, CharacterSize, CharacterAlignment

players_db = {
    1: Player(
        id=1,
        name="Silviana Moonleaf",
        appearance="Graceful elf with silver hair braided with leaves, violet eyes, and elegant elven robes",
        race=CharacterRace.ELF.value,
        class_name=PlayerClass.WIZARD.value,
        size=CharacterSize.MEDIUM.value,
        alignment=CharacterAlignment.NEUTRAL_GOOD.value
    ),
    2: Player(
        id=2,
        name="Pippin Greenhill",
        appearance="Cheerful hobbit with curly auburn hair, bright brown eyes, and well-worn traveling clothes",
        race=CharacterRace.HALFLING.value,
        class_name=PlayerClass.ROGUE.value,
        size=CharacterSize.SMALL.value,
        alignment=CharacterAlignment.CHAOTIC_GOOD.value
    )
}

next_player_id = 3
