from app.models.encounter import EncounterCreate

encounters_db = [
    # Upper Deck
    EncounterCreate(
        user_id=1,
        world_id=1,
        name="The Upper Deck",
        description="The ship's command center rises above the main deck, offering a commanding view of the seas. The wheel stands at the stern, brass fittings gleaming. Charts and navigation instruments are secured nearby. Rope ladders provide access to the crow's nest above, while a companionway leads down to the main deck.",
        position_x=500.0,
        position_y=-50.0,
        character_ids=[5, 3],  # Gregor, Finnian 'Finn' Swift
        player_ids=[1],  # Sir Alaric
    ),
    # Main Deck
    EncounterCreate(
        user_id=1,
        world_id=1,
        name="The Main Deck",
        description="The heart of ship activity, this weathered deck stretches bow to stern under open sky. Salt-stained planks creak as the ship rolls with waves. Thick ropes and rigging crisscross overhead, while barrels are secured along the sides. At the stern, an ornate door marks the captain's quarters.",
        position_x=500.0,
        position_y=400.0,
        character_ids=[1],  # Barthus
        player_ids=[0],  # Mira
    ),
    # Captain's Quarters
    EncounterCreate(
        user_id=1,
        world_id=1,
        name="The Captain's Quarters",
        description="Captain's private sanctuary at the ship's stern features polished mahogany paneling and brass fittings that gleam in lamplight. A large chart table dominates the center, covered with maps and instruments. Behind a writing desk sits a leather chair, while a locked sea chest rests in the corner.",
        position_x=1150.0,
        position_y=400.0,
        character_ids=[0],  # Captain
        player_ids=[],  # No players in Captain's Quarters
    ),
    # The Hold
    EncounterCreate(
        user_id=1,
        world_id=1,
        name="The Hold",
        description="The ship's deepest storage area stretches into shadowy recesses, filled with musty smells of damp wood and goods. Wooden crates and barrels are stacked high against the hull, secured with rope. Water barrels, grain sacks, and spare rope fill every space. In the far corner, one crate wrapped in oilcloth and chains sits isolated, emanating a faint hum.",
        position_x=500.0,
        position_y=1300.0,
        character_ids=[6],  # Lady Seraphina Valerius
        player_ids=[4],  # Elaris (rl_name James)
    ),
    # Crew Quarters
    EncounterCreate(
        user_id=1,
        world_id=1,
        name="The Crew Quarters",
        description="The cramped living space stretches beneath low beams, barely tall enough to stand. Hammocks swing in tiers from every beam, creating a maze of sleeping spaces. Sea chests line the walls with sailors' possessions. The air is thick with scents of bodies, tobacco, and tar. Personal mementos are scattered about.",
        position_x=1150.0,
        position_y=767.0,
        character_ids=[3, 4],  # Finnian 'Finn' Swift, Mara
        player_ids=[2],  # Thalion
    ),
    # Lower Deck
    EncounterCreate(
        user_id=1,
        world_id=1,
        name="The Lower Deck",
        description="The lower deck serves as the main thoroughfare beneath the main deck, dimly lit by swaying lanterns that cast dancing shadows. The ceiling is low, forcing taller crew to duck. The air is thick with aromas of Mara's cooking from the galley, tar, and sea smell.",
        position_x=500.0,
        position_y=830.0,
        character_ids=[2],  # Silas
        player_ids=[3],  # Brynja
    )
]
