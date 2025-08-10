from app.models.memory import Memory

memories_db = {
    1: Memory(
        id=1, 
        content="Remembers the ancient prophecy about the chosen one who will unite the kingdoms",
        character_ids=[1, 2]
    ),
    2: Memory(
        id=2,
        content="Witnessed the great battle at Silverbrook where the dragon was defeated",
        character_ids=[1]
    ),
}

next_memory_id = 3