from app.models.memory import Memory

memories_db = {
    1: Memory(
        id=1,
        user_id=1,
        world_id=1,
        title="The Old Took's Tale",
        content="Recalls the story of Old Took's adventure beyond the Shire, when he ventured to the Lonely Mountain and returned with tales of dwarven halls and distant lands",
        character_ids=[1, 2]
    ),
    2: Memory(
        id=2,
        user_id=1,
        world_id=1,
        title="The Great Harvest Festival",
        content="Remembers the legendary harvest festival at Hobbiton where the entire Shire gathered, and Farmer Maggot's prize-winning pumpkins were stolen by mysterious folk",
        character_ids=[1, 2]
    ),
}

next_memory_id = 3