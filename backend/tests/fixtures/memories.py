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
        content="Word is the captain's been acting more secretive than usual this voyage. Keeps checking on a particular crate in the hold, won't let anyone near it. Old Salty says he saw strange markings on it - ancient looking. Mara heard from the quartermaster that we're getting triple rates for this run, which ain't normal for textiles and spices.",
        character_ids=[0, 1, 2, 3, 4, 5, 6]  # All crew members
    ),
    MemoryCreate(
        user_id=1,
        world_id=1,
        title="Time at Sea",
        content="Most of us have been sailing together for at least two years now, except young Finn who joined us six months back in Neverwinter. The captain's had this ship for five years, and Barthus has been with him since the beginning. Old Salty's been on these waters for thirty years, though only the last three with us.",
        character_ids=[0, 1, 2, 3, 4, 5, 6]  # All crew members
    ),
    MemoryCreate(
        user_id=1,
        world_id=1,
        title="Our Current Passengers",
        content="We've taken on some passengers in Neverwinter - a mixed group of adventurers by the look of them. There's a halfling woman with quick eyes, a human in shining mail who carries himself like nobility, an elf fighter with more weapons than sense, a dwarf priestess with a holy symbol, and another elf who looks like a scholar. They paid well for passage and keep mostly to themselves, though they've been asking questions about the ship and cargo.",
        character_ids=[0, 1, 2, 3, 4, 5, 6]  # All crew members
    ),
    
    # Individual character memories
    
    # Captain Elias Thorne (character_id: 0)
    MemoryCreate(
        user_id=1,
        world_id=1,
        title="Noble Obligations",
        content="My cousin in Waterdeep writes that the family estate may go to auction if I cannot produce 5,000 gold pieces by summer's end. This cargo run must succeed. I've staked everything on it, including taking on those adventurers as passengers despite my misgivings about their intentions.",
        character_ids=[0]  # Captain only
    ),
    
    # Barthus 'The Bull' Ironhand (character_id: 1)
    MemoryCreate(
        user_id=1,
        world_id=1,
        title="Loyalty to the Captain",
        content="Captain Thorne gave me a second chance when the city watch cast me out. I was nobody - just another thug who hit too hard. Now I'm quartermaster on a proper merchant vessel. I'd die before I let anyone threaten the captain or his cargo.",
        character_ids=[1]  # Barthus only
    ),
    MemoryCreate(
        user_id=1,
        world_id=1,
        title="Suspicious Passengers",
        content="Those adventurers we took on... I don't like how they've been nosing around. Caught the halfling near the cargo hold yesterday. The elf wizard's been asking too many questions about our route and schedule. I've doubled the watch on the hold.",
        character_ids=[1]  # Barthus only
    ),
    
    # Silas 'Salty' Croft (character_id: 2)
    MemoryCreate(
        user_id=1,
        world_id=1,
        title="Old Sailor's Intuition",
        content="In thirty years at sea, I've learned to read the signs. This voyage feels different. The captain's nervous as a cat in a storm, and that crate in the hold... I swear I heard something humming from it during the middle watch. Mark my words, there's more than textiles in our hold.",
        character_ids=[2]  # Salty only
    ),
    MemoryCreate(
        user_id=1,
        world_id=1,
        title="Side Business",
        content="I've got a small package hidden in my sea chest - some Moonshae tobacco for my contact in Waterdeep. Nothing major, just enough to supplement my wages. Been doing these small runs for years. The captain don't know, and what he don't know won't hurt him.",
        character_ids=[2]  # Salty only
    ),
    
    # Finnian 'Finn' Swift (character_id: 3)
    MemoryCreate(
        user_id=1,
        world_id=1,
        title="Dreams of Adventure",
        content="Six months ago I was mending nets in Thistledown village. Now I'm sailing the Sword Coast! The other sailors tell such tales - pirates, sea monsters, lost treasures. Maybe one day I'll have stories of my own. For now, I just try not to embarrass myself in the rigging.",
        character_ids=[3]  # Finn only
    ),
    MemoryCreate(
        user_id=1,
        world_id=1,
        title="Fear of Gregor",
        content="Gregor One-Eye cornered me in the hold last week, said he'd teach me 'how things really work at sea.' The way he smiled made my skin crawl. I've been avoiding him since, volunteering for every watch aloft just to stay clear of him.",
        character_ids=[3]  # Finn only
    ),
    
    # Mara Stone (character_id: 4)
    MemoryCreate(
        user_id=1,
        world_id=1,
        title="The Galley Network",
        content="Everyone comes to my galley eventually - for food, for warmth, for someone to listen. I hear everything that happens on this ship. The captain's worried about something in the hold, Barthus is on edge, and those passengers... the dwarf priestess seems kind enough, but the others are definitely up to something.",
        character_ids=[4]  # Mara only
    ),
    MemoryCreate(
        user_id=1,
        world_id=1,
        title="Feeding the Crew",
        content="Twenty souls to feed, three meals a day, and supplies running lower than I'd like. We should have restocked more in Neverwinter, but the captain was in a hurry to sail. I'll make do - always have. But if we hit bad weather and delays, we'll be on half rations before Waterdeep.",
        character_ids=[4]  # Mara only
    ),
    
    # Gregor 'One-Eye' Nilsen (character_id: 5)
    MemoryCreate(
        user_id=1,
        world_id=1,
        title="The Old Days",
        content="I miss the freedom of the pirate life - taking what you want, answering to no one. But the Waterdhavian navy has gotten too good, too organized. Better to hide in plain sight on a merchant vessel. Still, if the right opportunity presents itself... that mysterious cargo might be worth more than my wages.",
        character_ids=[5]  # Gregor only
    ),
    MemoryCreate(
        user_id=1,
        world_id=1,
        title="Watching for Weakness",
        content="The halfling passenger - she moves like a thief. Takes one to know one. I've been watching her, and she's definitely casing the ship. Maybe we can come to an arrangement, or maybe I'll just wait and take whatever she finds. Young Finn would make good bait if I need a distraction.",
        character_ids=[5]  # Gregor only
    ),
    
    # Lady Seraphina Valerius (character_id: 6)
    MemoryCreate(
        user_id=1,
        world_id=1,
        title="The Real Mission",
        content="My contacts in Neverwinter were quite specific - Captain Thorne is transporting something of great value, something that certain parties in Waterdeep would pay handsomely to acquire. I must maintain my cover as a textile merchant while determining what lies in that heavily guarded crate.",
        character_ids=[6]  # Lady Valerius only
    ),
    MemoryCreate(
        user_id=1,
        world_id=1,
        title="Observing the Passengers",
        content="These adventurers are not mere travelers. The way they coordinate their movements, their subtle signals... they're planning something. The halfling has been scouting, the paladin provides distraction with his noble bearing, while the others gather information. They might prove useful - or problematic - to my own plans.",
        character_ids=[6]  # Lady Valerius only
    ),
]