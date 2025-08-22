from app.models.reveal import RevealCreate

reveal_db = [
    RevealCreate(
        user_id=1,
        world_id=1,
        title="Whispers in the Rigging",
        character_ids=[1, 2, 3, 4, 5],  # All crew except captain and Lady Valerius
        level_1_content="Word is the captain's been acting more secretive than usual this voyage. Keeps checking on a particular crate in the hold, won't let anyone near it.",
        level_2_content="Old Salty says he saw strange markings on the crate - ancient looking, like nothing from the Sword Coast. Mara heard from the quartermaster that we're getting triple rates for this run, which ain't normal for textiles and spices.",
        level_3_content="The crate's about three feet long, wrapped in oilcloth and chains. It hums sometimes at night - Finn swears he heard it when he was on watch. Whatever's in there, it's not natural.",
        standard_threshold=0,  # Always available
        privileged_threshold=10,  # Easy
        exclusive_threshold=15  # Medium
    ),
    
    RevealCreate(
        user_id=1,
        world_id=1,
        title="The Bull's Devotion",
        character_ids=[1],  # Barthus only
        level_1_content="Barthus 'The Bull' owes everything to Captain Thorne. The captain gave him a respectable position when no one else would hire him after his dismissal from the city watch.",
        level_2_content="Barthus was dismissed for beating a merchant nearly to death over an insult. The captain not only hired him but pays him double wages. He'd die before betraying Thorne.",
        level_3_content="The quartermaster has orders to flood the cargo hold if anyone tries to steal the captain's special cargo. He keeps a hammer near the hull plugs at all times.",
        standard_threshold=5,  # Very Easy
        privileged_threshold=15,  # Medium
        exclusive_threshold=20  # Hard
    ),
    
    RevealCreate(
        user_id=1,
        world_id=1,
        title="Smuggler's Wisdom",
        character_ids=[2],  # Salty only
        level_1_content="Old Salty's been sailing these waters for thirty years. He knows every cove, every hidden inlet, and every corrupt port official from here to Baldur's Gate.",
        level_2_content="Salty runs a small smuggling operation on the side - nothing major, just tobacco, spices, and the occasional bottle of Moonshae whiskey. He has contacts in every major port.",
        level_3_content="For the right price, Salty knows how to get into the cargo hold without alerting the watch. There's a loose plank near the galley that leads to a crawlspace. He's used it before to stash his own goods.",
        standard_threshold=5,  # Very Easy
        privileged_threshold=10,  # Easy
        exclusive_threshold=15  # Medium
    ),
    
    RevealCreate(
        user_id=1,
        world_id=1,
        title="Galley Gossip",
        character_ids=[4],  # Mara only
        level_1_content="Everyone talks in the galley. Mara hears everything - who's feuding, who's stealing extra rations, who's planning what. She knows this ship better than anyone except maybe the captain.",
        level_2_content="Mara noticed the captain's been taking his meals in his cabin since leaving Neverwinter. He's also been burning papers - she's seen the ash when collecting his dishes. Something's got him spooked.",
        level_3_content="The captain keeps a hidden compartment behind his bunk. Mara saw him checking it when she brought his breakfast unexpectedly. There's a key on a chain around his neck that he never removes, not even when bathing.",
        standard_threshold=0,  # Always available
        privileged_threshold=10,  # Easy
        exclusive_threshold=15  # Medium
    ),
    
    RevealCreate(
        user_id=1,
        world_id=1,
        title="A Pirate's Instinct",
        character_ids=[5],  # Gregor only
        level_1_content="Gregor One-Eye can smell opportunity like a shark smells blood. This voyage reeks of it. The captain's nervous, the passengers are too curious, and that cargo's worth more than the ship itself.",
        level_2_content="In his pirate days, Gregor once saw a similar crate on a Calishite vessel. It held a djinn's lamp worth a king's ransom. Whatever Thorne's carrying, it's magical and it's valuable. Very valuable.",
        level_3_content="Gregor's been planning his own heist. During the next storm, when everyone's distracted, he'll make his move. He's already loosened some boards in the hold and has a small boat ready to lower. If someone else tries for the cargo first, he might be willing to... negotiate.",
        standard_threshold=10,  # Easy
        privileged_threshold=15,  # Medium
        exclusive_threshold=20  # Hard
    ),
    
    RevealCreate(
        user_id=1,
        world_id=1,
        title="Noble Intrigue",
        character_ids=[6],  # Lady Valerius only
        level_1_content="Lady Seraphina Valerius claims to be a textile merchant, but she moves with too much grace, observes too keenly, and her hands are too soft for someone who handles cloth all day.",
        level_2_content="She's been asking subtle questions about the ship's route, its stops, and its cargo manifest. She's particularly interested in any unscheduled stops or changes to the itinerary. Her cabin contains several books on ancient artifacts and maritime law.",
        level_3_content="Lady Valerius is an agent of the Waterdhavian noble houses. She's been hired to acquire the artifact before it reaches its buyer. She has a sleep poison that could knock out the entire crew, and a sending stone to signal her associates when the time is right.",
        standard_threshold=10,  # Easy
        privileged_threshold=15,  # Medium
        exclusive_threshold=25  # Very Hard
    ),
    
    RevealCreate(
        user_id=1,
        world_id=1,
        title="The Captain's Secret",
        character_ids=[0],  # Captain only
        level_1_content="My cousin in Waterdeep writes that the family estate may go to auction if I cannot produce 5,000 gold pieces by summer's end. This cargo run must succeed. I've staked everything on it, including taking on those adventurers as passengers despite my misgivings about their intentions.",
        level_2_content="The captain owes 5,000 gold pieces to save his family estate from auction. This special cargo run is his last chance. He's transporting an ancient artifact - the Eye of Storms, a powerful magical orb that controls weather - to a collector in Waterdeep who promised enough gold to save everything.",
        level_3_content="The Eye of Storms is one of three artifacts created by the storm giant king Hekaton centuries ago. It can summon hurricanes, part seas, and control the winds. The 'collector' is actually a cult of Talos, god of storms, who plan to use it to terrorize the Sword Coast. Thorne doesn't know this - he's desperate and didn't ask questions. The artifact is in a lead-lined box warded against divination, hidden inside the marked crate. The key around his neck opens both the box and a magical seal that will destroy the artifact if forced.",
        standard_threshold=20,  # Hard
        privileged_threshold=25,  # Very Hard
        exclusive_threshold=30  # Nearly Impossible
    )
]
