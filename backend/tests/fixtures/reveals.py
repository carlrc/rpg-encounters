from app.models.reveal import RevealCreate

reveal_db = [
    RevealCreate(
        user_id=1,
        world_id=1,
        title="Whispers in the Rigging",
        character_ids=[1, 2, 3, 4, 5],  # All crew except captain and Lady Valerius
        level_1_content="I've noticed the captain's been acting more secretive than usual this voyage. He keeps checking on a particular crate in the hold, won't let anyone near it.",
        level_2_content="Old Salty told me he saw strange markings on the crate - ancient looking, like nothing from the Sword Coast. Mara mentioned she heard from the quartermaster that we're getting triple rates for this run, which ain't normal for textiles and spices.",
        level_3_content="I've seen that crate - it's about three feet long, wrapped in oilcloth and chains. It hums sometimes at night. Finn swears he heard it when he was on watch. Whatever's in there, it's not natural.",
        standard_threshold=0,  # Always available
        privileged_threshold=10,  # Easy
        exclusive_threshold=15  # Medium
    ),
    
    RevealCreate(
        user_id=1,
        world_id=1,
        title="The Bull's Devotion",
        character_ids=[1],  # Barthus only
        level_1_content="I owe everything to Captain Thorne. He gave me a respectable position when no one else would hire me after my dismissal from the city watch.",
        level_2_content="I was dismissed for beating a merchant nearly to death over an insult. The captain not only hired me but pays me double wages. I'd die before betraying Thorne.",
        level_3_content="I have orders to flood the cargo hold if anyone tries to steal the captain's special cargo. I keep a hammer near the hull plugs at all times.",
        standard_threshold=5,  # Very Easy
        privileged_threshold=15,  # Medium
        exclusive_threshold=20  # Hard
    ),
    
    RevealCreate(
        user_id=1,
        world_id=1,
        title="Smuggler's Wisdom",
        character_ids=[2],  # Salty only
        level_1_content="I've been sailing these waters for thirty years. I know every cove, every hidden inlet, and every corrupt port official from here to Baldur's Gate.",
        level_2_content="I run a small smuggling operation on the side - nothing major, just tobacco, spices, and the occasional bottle of Moonshae whiskey. I have contacts in every major port.",
        level_3_content="For the right price, I know how to get into the cargo hold without alerting the watch. There's a loose plank near the galley that leads to a crawlspace. I've used it before to stash my own goods.",
        standard_threshold=5,  # Very Easy
        privileged_threshold=10,  # Easy
        exclusive_threshold=15  # Medium
    ),
    
    RevealCreate(
        user_id=1,
        world_id=1,
        title="Galley Gossip",
        character_ids=[4],  # Mara only
        level_1_content="Everyone talks in the galley. I hear everything - who's feuding, who's stealing extra rations, who's planning what. I know this ship better than anyone except maybe the captain.",
        level_2_content="I've noticed the captain's been taking his meals in his cabin since leaving Neverwinter. He's also been burning papers - I've seen the ash when collecting his dishes. Something's got him spooked.",
        level_3_content="The captain keeps a hidden compartment behind his bunk. I saw him checking it when I brought his breakfast unexpectedly. There's a key on a chain around his neck that he never removes, not even when bathing.",
        standard_threshold=0,  # Always available
        privileged_threshold=10,  # Easy
        exclusive_threshold=15  # Medium
    ),
    
    RevealCreate(
        user_id=1,
        world_id=1,
        title="A Pirate's Instinct",
        character_ids=[5],  # Gregor only
        level_1_content="I can smell opportunity like a shark smells blood. This voyage reeks of it. The captain's nervous, the passengers are too curious, and that cargo's worth more than the ship itself.",
        level_2_content="In my pirate days, I once saw a similar crate on a Calishite vessel. It held a djinn's lamp worth a king's ransom. Whatever Thorne's carrying, it's magical and it's valuable. Very valuable.",
        level_3_content="I've been planning my own heist. During the next storm, when everyone's distracted, I'll make my move. I've already loosened some boards in the hold and have a small boat ready to lower. If someone else tries for the cargo first, I might be willing to... negotiate.",
        standard_threshold=10,  # Easy
        privileged_threshold=15,  # Medium
        exclusive_threshold=20  # Hard
    ),
    
    RevealCreate(
        user_id=1,
        world_id=1,
        title="Noble Intrigue",
        character_ids=[6],  # Lady Valerius only
        level_1_content="I'm a simple merchant traveling to waterdeep to partake in the famous markets.",
        level_2_content="My contacts in Neverwinter were quite specific about Captain Thorne transporting something of great value.",
        level_3_content="I'm an agent of the Waterdhavian noble houses. I've been hired to acquire the artifact before it reaches its buyer - my contacts informed me that certain parties in Waterdeep would pay handsomely to acquire whatever lies in that heavily guarded crate. I have a sleep poison that could knock out the entire crew, and a sending stone to signal my associates when the time is right.",
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
