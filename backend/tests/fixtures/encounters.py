from app.models.encounter import EncounterCreate

encounters_db = [
    # Upper Deck
    EncounterCreate(
        user_id=1,
        world_id=1,
        name="The Upper Deck",
        description="The ship's command center rises above the main deck, offering a commanding view of the surrounding seas. The ship's wheel stands prominently at the stern, its brass fittings gleaming despite the salt air. Charts and navigation instruments are secured in a weatherproof case nearby. Old Salty often paces this elevated platform, barking orders to the crew below. Rope ladders and rigging provide access to the crow's nest high above, while a steep companionway leads down to the main deck below. The wind is stronger here, and you can see for miles across the endless ocean.",
        position_x=200.0,
        position_y=0.0,
        character_ids=[5]  # Mara Stone
    ),
    # Main Deck
    EncounterCreate(
        user_id=1,
        world_id=1,
        name="The Main Deck",
        description="The heart of the ship's activity, this weathered wooden deck stretches from bow to stern under the open sky. Salt-stained planks creak beneath your feet as the ship rolls with the waves. Thick ropes and rigging crisscross overhead, while barrels and coils of rope are secured along the sides. A steep companionway leads up to the upper deck where the helm awaits. A heavy forward hatch opens to the lower deck below. At the stern, an ornate door marks the entrance to the captain's private quarters. The main mast towers above, its sails catching the ocean wind.",
        position_x=200.0,
        position_y=300.0,
        character_ids=[1]  # Captain Elias Thorne
    ),
    # Captain's Quarters
    EncounterCreate(
        user_id=1,
        world_id=1,
        name="The Captain's Quarters",
        description="Captain E. Thorne's private sanctuary occupies the ship's stern, featuring polished mahogany paneling and brass fittings that gleam in the lamplight. A large chart table dominates the center, covered with navigational maps, compass, and sextant. Behind an ornate writing desk sits a high-backed leather chair, while a locked sea chest rests in the corner, its iron bands suggesting valuable contents. Shelves line the walls, holding leather-bound logbooks, bottles of fine rum, and curious artifacts from distant ports. A small porthole offers a view of the ship's wake, and the faint smell of tobacco and parchment fills the air. An ornate door leads back to the main deck.",
        position_x=600.0,
        position_y=300.0,
        character_ids=[]
    ),
    # The Hold
    EncounterCreate(
        user_id=1,
        world_id=1,
        name="The Hold",
        description="The ship's deepest storage area stretches into shadowy recesses, filled with the musty smell of damp wood and stored goods. Wooden crates and iron-bound barrels are stacked high against the curved hull, secured with thick rope to prevent shifting in rough seas. Water barrels, sacks of grain, and coils of spare rope fill every available space. In the far corner, one particular crate wrapped in oilcloth and heavy chains sits isolated from the rest, emanating an almost imperceptible hum that seems to resonate through the ship's timbers. A heavy grated hatch above provides access back up to the lower deck, and rats scurry between the shadows.",
        position_x=200.0,
        position_y=900.0,
        character_ids=[]
    ),
    # Crew Quarters
    EncounterCreate(
        user_id=1,
        world_id=1,
        name="The Crew Quarters",
        description="The cramped living space of the ship's crew stretches beneath the low deck beams, barely tall enough for a man to stand upright. Hammocks swing in tiers from every available beam, creating a maze of sleeping spaces that sway with the ship's motion. Weathered sea chests line the walls, each containing a sailor's meager possessions. The air is thick with the mingled scents of unwashed bodies, pipe tobacco, damp wool, and tar. Personal mementos are scattered about - a carved bone whistle, a faded letter from home, a lucky coin nailed to a beam. In the darkest corner, Gregor One-Eye's hammock hangs alone, avoided by the other crew members. Near the galley wall, a loose plank in the flooring catches your attention. A doorway leads back to the lower deck.",
        position_x=600.0,
        position_y=600.0,
        character_ids=[3, 4, 6, 7]  # Silas 'Salty' Croft, Finnian 'Finn' Swift, Gregor 'One-Eye' Nilsen, Lady Seraphina Valerius
    ),
    # Lower Deck
    EncounterCreate(
        user_id=1,
        world_id=1,
        name="The Lower Deck",
        description="The ship's lower deck serves as the main thoroughfare beneath the main deck, dimly lit by swaying oil lanterns that cast dancing shadows on the wooden walls. The ceiling is low, forcing taller crew members to duck as they move about. The air is thick with the mingled aromas of Mara's cooking from the nearby galley, tar from rope maintenance, and the ever-present smell of the sea. Wooden support beams run the length of the deck, and coils of rope, spare canvas, and ship supplies are stored in every available nook. A doorway leads to the cramped crew quarters, while a heavy grated hatch provides access down to the cargo hold below. A ladder leads up through the forward hatch to the main deck above, where natural light filters down.",
        position_x=200.0,
        position_y=600.0,
        character_ids=[2]  # Barthus 'The Bull' Ironhand
    )
]