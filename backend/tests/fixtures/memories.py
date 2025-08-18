from app.models.memory import MemoryCreate

memories_db = [
    MemoryCreate(
        user_id=1,
        world_id=1,
        title="The Old Took's Tale",
        content="Recalls the story of Old Took's adventure beyond the Shire, when he ventured to the Lonely Mountain and returned with tales of dwarven halls and distant lands",
        character_ids=[0, 1]  # Bingo Bracegirdle and Old Took (array indices)
    ),
    MemoryCreate(
        user_id=1,
        world_id=1,
        title="The Great Harvest Festival",
        content="Remembers the legendary harvest festival at Hobbiton where the entire Shire gathered, and Farmer Maggot's prize-winning pumpkins were stolen by mysterious folk",
        character_ids=[0, 1]  # Bingo Bracegirdle and Old Took (array indices)
    ),
]