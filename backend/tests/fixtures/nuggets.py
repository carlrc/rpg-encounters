from typing import Dict
from app.models.nugget import Reveal

reveal_db: Dict[int, Reveal] = {
    1: Reveal(
        id=1,
        title="The Garden Vandal",
        character_ids=[1, 3, 4],
        level_1_content="There is someone vandalizing the towns gardens",
        level_2_content="It's a local. Not a foreigner as everyone expects.",
        level_3_content="It's Merry Greenhill vandalizing the gardens",
    ),
    2: Reveal(
        id=2,
        title="Available Rooms",
        character_ids=[1],
        level_1_content="For normal customers, the Inn has only 1 standard single bed room left for the evening.",
        level_2_content="For trusted customers, the Inn has a suite with a balcony available.",
        level_3_content="For important customers, a secret suite is available with a secret corridor which connects to all the rooms.",
    )
}


next_reveal_id = 2
