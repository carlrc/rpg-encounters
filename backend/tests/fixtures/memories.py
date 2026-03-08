from app.models.memory import MemoryCreate

memories_db = [
    # Core memories (all crew members)
    MemoryCreate(
        user_id=1,
        world_id=1,
        title="The Siren's Call",
        content="Our vessel, The Siren's Call, is a sturdy three-masted merchant carrack. She's been sailing the Sword Coast for near a decade now, carrying goods between Neverwinter and Waterdeep. The ship has an upper deck, main deck with the captain's quarters, lower deck with crew quarters, and a hold below for cargo.",
        character_ids=[0, 1, 2, 3, 4, 5, 6]  # All crew members
    ),
    MemoryCreate(
        user_id=1,
        world_id=1,
        title="Captain Thorne's Command",
        content="Captain Elias Thorne runs a tight ship. He's a stern man from a noble family, always proper in his speech and bearing. The captain keeps mostly to his quarters or the helm, rarely mixing with common crew. Some say he's trying to restore his family's lost fortune through these merchant runs.",
        character_ids=[0, 1, 2, 3, 4, 5, 6]  # All crew members
    ),
    MemoryCreate(
        user_id=1,
        world_id=1,
        title="Our Motley Crew",
        content="We've got Barthus 'The Bull' as quartermaster - mean as a wounded bear and twice as strong. Old Salty Croft is our boatswain, knows every superstition and sea tale. Young Finn Swift works the rigging, green as seaweed but eager. Mara Stone runs the galley with an iron ladle, and Gregor One-Eye... well, best to stay clear of him. Then there's that mysterious Lady Valerius, keeps to her cabin mostly.",
        character_ids=[0, 1, 2, 3, 4, 5, 6]  # All crew members
    ),
    MemoryCreate(
        user_id=1,
        world_id=1,
        title="Whispers in the Rigging",
        content="Word is the captain's been acting more secretive than usual this voyage. Keeps checking on a particular crate in the hold, won't let anyone near it. Mara heard from the quartermaster that we're getting triple rates for this run, which ain't normal for textiles and spices.",
        character_ids=[0, 1, 2, 3, 4, 5, 6]  # All crew members
    ),
    MemoryCreate(
        user_id=1,
        world_id=1,
        title="Time at Sea",
        content="Most of us have been sailing together for at least two years now, except young Finn who joined us six months back in Neverwinter. The captain's had this ship for five years, and Barthus has been with him since the beginning. Old Salty's been on these waters for thirty years, though only the last three with us.",
        character_ids=[0, 1, 2, 3, 4, 5, 6]  # All crew members
    ),
    
    # Individual character memories
    # Barthus 'The Bull' Ironhand (character_id: 1)
    MemoryCreate(
        user_id=1,
        world_id=1,
        title="Loyalty to the Captain",
        content="Captain Thorne gave me a second chance when the city watch cast me out. I was nobody - just another thug who hit too hard. Now I'm quartermaster on a proper merchant vessel. I'd die before I let anyone threaten the captain or his cargo.",
        character_ids=[1]  # Barthus only
    )

]