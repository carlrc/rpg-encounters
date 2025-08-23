from app.models.encounter import EncounterCreate

encounters_db = [
    # Upper Deck
    EncounterCreate(
        user_id=1,
        world_id=1,
        name="The Upper Deck",
        description="The ship's command center rises above the main deck, offering a commanding view of the seas. The wheel stands at the stern, brass fittings gleaming. Charts and navigation instruments are secured nearby. Old Salty paces this platform, barking orders to the crew below. Rope ladders provide access to the crow's nest above, while a companionway leads down to the main deck. The wind is stronger here.",
        position_x=200.0,
        position_y=0.0,
        character_ids=[5]  # Mara Stone
    ),
    # Main Deck
    EncounterCreate(
        user_id=1,
        world_id=1,
        name="The Main Deck",
        description="The heart of ship activity, this weathered deck stretches bow to stern under open sky. Salt-stained planks creak as the ship rolls with waves. Thick ropes and rigging crisscross overhead, while barrels are secured along the sides. A companionway leads up to the upper deck. A forward hatch opens to the lower deck below. At the stern, an ornate door marks the captain's quarters. The main mast towers above.",
        position_x=200.0,
        position_y=300.0,
        character_ids=[1]  # Captain Elias Thorne
    ),
    # Captain's Quarters
    EncounterCreate(
        user_id=1,
        world_id=1,
        name="The Captain's Quarters",
        description="Captain Thorne's private sanctuary at the ship's stern features polished mahogany paneling and brass fittings that gleam in lamplight. A large chart table dominates the center, covered with maps and instruments. Behind a writing desk sits a leather chair, while a locked sea chest rests in the corner. Shelves hold logbooks and artifacts. A porthole offers a view of the wake. An ornate door leads out.",
        position_x=600.0,
        position_y=300.0,
        character_ids=[]
    ),
    # The Hold
    EncounterCreate(
        user_id=1,
        world_id=1,
        name="The Hold",
        description="The ship's deepest storage area stretches into shadowy recesses, filled with musty smells of damp wood and goods. Wooden crates and barrels are stacked high against the hull, secured with rope. Water barrels, grain sacks, and spare rope fill every space. In the far corner, one crate wrapped in oilcloth and chains sits isolated, emanating a faint hum. A grated hatch above provides access to the lower deck.",
        position_x=200.0,
        position_y=900.0,
        character_ids=[]
    ),
    # Crew Quarters
    EncounterCreate(
        user_id=1,
        world_id=1,
        name="The Crew Quarters",
        description="The cramped living space stretches beneath low beams, barely tall enough to stand. Hammocks swing in tiers from every beam, creating a maze of sleeping spaces. Sea chests line the walls with sailors' possessions. The air is thick with scents of bodies, tobacco, and tar. Personal mementos are scattered about. In the darkest corner, Gregor's hammock hangs alone. Near the galley, a loose plank catches attention. A doorway leads out.",
        position_x=600.0,
        position_y=600.0,
        character_ids=[3, 4, 6, 7]  # Silas 'Salty' Croft, Finnian 'Finn' Swift, Gregor 'One-Eye' Nilsen, Lady Seraphina Valerius
    ),
    # Lower Deck
    EncounterCreate(
        user_id=1,
        world_id=1,
        name="The Lower Deck",
        description="The lower deck serves as the main thoroughfare beneath the main deck, dimly lit by swaying lanterns that cast dancing shadows. The ceiling is low, forcing taller crew to duck. The air is thick with aromas of Mara's cooking from the galley, tar, and sea smell. Wooden beams run the deck's length. A doorway leads to crew quarters, while a grated hatch provides access to the cargo hold. A ladder leads up.",
        position_x=200.0,
        position_y=600.0,
        character_ids=[2]  # Barthus 'The Bull' Ironhand
    )
]