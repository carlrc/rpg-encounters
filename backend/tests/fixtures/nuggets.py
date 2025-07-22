from typing import Dict
from app.models.nugget import TrustNugget

nugget_db: Dict[int, TrustNugget] = {
    1: TrustNugget(
        id=1,
        title="The Garden Vandal",
        character_ids=[1, 3, 4],
        level_1_content="There is someone vandalizing the towns gardens",
        level_2_content="It's a local. Not a foreigner as everyone expects.",
        level_3_content="It's Merry Greenhill vandalizing the gardens",
    )
}


next_nugget_id = 2
