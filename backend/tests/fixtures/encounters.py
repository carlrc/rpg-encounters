from app.models.encounter import Encounter

encounters_db = {
    1: Encounter(
        id=1,
        name="The Prancing Pony Tavern",
        description="A cozy tavern filled with the warm glow of candlelight and the cheerful chatter of patrons. The air is thick with the aroma of roasted meat and ale. Bingo Bracegirdle runs this establishment with pride.",
        position_x=200.0,
        position_y=150.0,
        characters=[1, 2]  # Bingo Bracegirdle and Old Took
    ),
    2: Encounter(
        id=2,
        name="Village Square",
        description="The heart of the village where merchants set up their stalls and villagers gather to share news. A large oak tree provides shade in the center, with wooden benches arranged around it.",
        position_x=500.0,
        position_y=150.0,
        characters=[3]  # Poppy Proudfoot
    ),
    3: Encounter(
        id=3,
        name="Community Gardens",
        description="Well-tended vegetable patches and herb gardens maintained by the village. Rows of crops stretch across the fertile ground, with a small tool shed and compost area nearby.",
        position_x=350.0,
        position_y=300.0,
        characters=[4]  # Merry Greenhill
    ),
    4: Encounter(
        id=4,
        name="Forest Path",
        description="A winding dirt path that leads through the dense woodland surrounding the village. Ancient trees tower overhead, their branches forming a natural canopy that filters the sunlight.",
        position_x=650.0,
        position_y=250.0,
        characters=[]
    )
}

next_encounter_id = 5