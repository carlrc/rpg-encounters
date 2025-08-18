from app.models.reveal import RevealCreate

reveal_db = [
    RevealCreate(
        user_id=1,
        world_id=1,
        title="The Garden Vandal",
        character_ids=[0, 2, 3],  # Bingo Bracegirdle, Poppy Proudfoot, Merry Greenhill (array indices)
        level_1_content="There is someone vandalizing the towns gardens",
        level_2_content="It's a local. Not a foreigner as everyone expects.",
        level_3_content="It's Merry Greenhill vandalizing the gardens",
    ),
    RevealCreate(
        user_id=1,
        world_id=1,
        title="Available Rooms",
        character_ids=[0],  # Bingo Bracegirdle (array index)
        level_1_content="For normal customers, the Inn has only 1 standard single bed room left for the evening.",
        level_2_content="For trusted customers, the Inn has a suite with a balcony available.",
        level_3_content="For important customers, a secret suite is available with a secret corridor which connects to all the rooms.",
    )
]
