from app.models.character import CharacterCreate
from app.models.race import Race, Size, Gender
from app.models.alignment import Alignment
from app.models.reveal import DifficultyClass
from app.models.class_traits import Class

characters_db = [
  CharacterCreate(
    user_id=1,
    world_id=1,
    name="Captain Elias Thorne",
    avatar=None,
    race=Race.HUMAN.value,
    size=Size.MEDIUM.value,
    alignment=Alignment.LAWFUL_NEUTRAL.value,
    gender=Gender.MALE.value,
    profession="Ship Captain",
    background="Born into a minor noble family that lost its fortune, Elias Thorne turned to the sea to reclaim his family's honor and wealth. He is a stern and pragmatic leader, respected and feared by his crew. He runs a tight ship and has no tolerance for nonsense.",
    communication_style="Uses formal, clipped nautical terms. He addresses the crew as 'men' or by their rank, never by name. For example: 'Mr. Croft, see to the main sail. Look lively now.' Does not engage in casual banter and expects his orders to be followed without question.",
    motivation="To restore his family's name and fortune, and to prove his worth as a captain and a nobleman. He is secretly transporting a valuable and ancient artifact to a wealthy collector in Waterdeep.",
    personality="Proud, ambitious, and deeply conscious of social status. He is courteous to nobles and patrons but disdainful of commoners and non-humans. He is meticulous and detail-oriented, especially when it comes to the ship's log and cargo manifests.",
    voice="JBFqnCBsd6RMkjVDRZzb",
    race_preferences={
      Race.HIGH_ELF.value: -2,
      Race.WOOD_ELF.value: -2,
      Race.HILL_DWARF.value: -1,
      Race.MOUNTAIN_DWARF.value: -1,
      Race.LIGHTFOOT_HALFLING.value: -1,
      Race.STOUT_HALFLING.value: -1,
      Race.FOREST_GNOME.value: -1,
      Race.ROCK_GNOME.value: -1,
      Race.HALF_ORC.value: -3,
      Race.DRAGONBORN.value: -2,
      Race.TIEFLING.value: -3,
      Race.HALF_ELF.value: -2
    },
    class_preferences={
      "Fighter": 1,
      "Paladin": 2,
      "Rogue": -2,
      "Warlock": -3,
      "Sorcerer": -1
    },
    gender_preferences={},
    size_preferences={}
  ),
  CharacterCreate(
    user_id=1,
    world_id=1,
    name="Barthus 'The Bull' Ironhand",
    avatar=None,
    race=Race.HUMAN.value,
    size=Size.MEDIUM.value,
    alignment=Alignment.TRUE_NEUTRAL.value,
    gender=Gender.MALE.value,
    profession="Quartermaster",
    background="A former city guard from a rough district, Barthus is as strong as an ox and twice as stubborn. He values order and discipline above all else. He's fiercely loyal to Captain Thorne, who gave him a respectable job after he was dismissed from the guard for excessive force.",
    communication_style="As an officer, he attempts to mimic the captain's formality but lacks his eloquence. He barks orders in short, guttural sentences. 'Get back to swabbing, you bilge rats!' He often peppers his speech with threats and insults.",
    motivation="To maintain order on the ship and protect the cargo at all costs. His loyalty to the captain is absolute, and he sees the ship's success as his own.",
    personality="Suspicious of outsiders and fiercely protective of the ship's stores. He is physically imposing and uses his presence to intimidate. He has a simple worldview, dividing people into 'useful' and 'useless'.",
    voice="JBFqnCBsd6RMkjVDRZzb",
    race_preferences={
      Race.HIGH_ELF.value: -1,
      Race.WOOD_ELF.value: -1,
      Race.HALF_ORC.value: -2,
      Race.TIEFLING.value: -2,
      Race.HALF_ELF.value: -1
    },
    class_preferences={
      "Barbarian": -2,
      "Rogue": -3
    },
    gender_preferences={},
    size_preferences={}
  ),
  CharacterCreate(
    user_id=1,
    world_id=1,
    name="Silas 'Salty' Croft",
    avatar=None,
    race=Race.HUMAN.value,
    size=Size.MEDIUM.value,
    alignment=Alignment.CHAOTIC_NEUTRAL.value,
    gender=Gender.MALE.value,
    profession="Boatswain",
    background="An old sailor who has spent more of his life on the sea than on land. He's seen it all and is deeply superstitious. He's responsible for the general maintenance of the ship and its equipment.",
    communication_style="Classic sailor speech, thick with slang and superstition. Calls people 'matey' or 'shipmate.' Often spins yarns and gives unsolicited advice. 'Mind the kraken's pull, lad. She's a fickle beast, the sea.'",
    motivation="To earn enough coin to retire comfortably in a quiet port town. He's not above a bit of smuggling on the side if the opportunity arises.",
    personality="Grizzled and weathered, with a twinkle in his eye. He's a gossip and knows every rumor circulating on the ship. He judges people by their ability to handle themselves on a ship, not by their birth.",
    voice="JBFqnCBsd6RMkjVDRZzb",
    race_preferences={
      Race.HILL_DWARF.value: 1,
      Race.MOUNTAIN_DWARF.value: 1,
      Race.FOREST_GNOME.value: -1,
      Race.ROCK_GNOME.value: -1
    },
    class_preferences={
      "Bard": 1,
      "Wizard": -1
    },
    gender_preferences={},
    size_preferences={}
  ),
  CharacterCreate(
    user_id=1,
    world_id=1,
    name="Finnian 'Finn' Swift",
    avatar=None,
    race=Race.HUMAN.value,
    size=Size.MEDIUM.value,
    alignment=Alignment.TRUE_NEUTRAL.value,
    gender=Gender.MALE.value,
    profession="Deckhand",
    background="A young man from a poor fishing village, trying to make a name for himself. He is agile and quick, known for his skill in climbing the rigging.",
    communication_style="Speaks with a thick, rural accent, often mumbling. He uses simple, un-nautical language unless repeating an order. He says 'aye' and 'right' a lot. He's not confident enough to engage in the typical sailor banter.",
    motivation="To see the world beyond his small village and perhaps find his fortune. He is impressionable and eager to prove his worth.",
    personality="Hardworking and diligent, but a bit naive. He is easily intimidated by the older crew members and is wary of strangers.",
    voice="JBFqnCBsd6RMkjVDRZzb",
    race_preferences={},
    class_preferences={},
    gender_preferences={},
    size_preferences={}
  ),
  CharacterCreate(
    user_id=1,
    world_id=1,
    name="Mara Stone",
    avatar=None,
    race=Race.HUMAN.value,
    size=Size.MEDIUM.value,
    alignment=Alignment.NEUTRAL_GOOD.value,
    gender=Gender.FEMALE.value,
    profession="Ship's Cook",
    background="Mara has worked on ships most of her life, following her father who was also a cook. She is tough and no-nonsense, but has a kind heart buried under a gruff exterior. The galley is her kingdom, and she rules it with an iron ladle.",
    communication_style="Shouts and curses like the saltiest of sailors, but with a maternal twist. 'Get this swill in ye before it gets cold, ye scurvy dogs!' Her compliments are as rare as a calm sea, but her insults are plentiful and creative.",
    motivation="To provide good, hearty meals for the crew and ensure everyone is well-fed and healthy. She feels a sense of responsibility for the crew's well-being.",
    personality="Motherly but stern. She is an excellent source of information, as everyone comes to her for food and tends to talk. She dislikes laziness and waste.",
    voice="JBFqnCBsd6RMkjVDRZzb",
    race_preferences={
      Race.LIGHTFOOT_HALFLING.value: 1,
      Race.STOUT_HALFLING.value: 1
    },
    class_preferences={
      "Cleric": 1
    },
    gender_preferences={},
    size_preferences={}
  ),
  CharacterCreate(
    user_id=1,
    world_id=1,
    name="Gregor 'One-Eye' Nilsen",
    avatar=None,
    race=Race.HUMAN.value,
    size=Size.MEDIUM.value,
    alignment=Alignment.CHAOTIC_EVIL.value,
    gender=Gender.MALE.value,
    profession="Deckhand",
    background="A former pirate who lost an eye in a raid. He managed to escape the noose and now works on merchant ships, biding his time. He is cruel and enjoys the suffering of others.",
    communication_style="A low, gravelly voice. He peppers his speech with guttural laughs and cruel jokes. He uses mockingly endearing terms like 'pal' or 'friend' before delivering a threat. 'Don't you worry your pretty little head about it, pal. Accidents happen at sea.'",
    motivation="Greed and self-preservation. He is always looking for an angle to exploit for personal gain and is not loyal to anyone but himself.",
    personality="A bully who preys on the weaker members of the crew like Finn. He is constantly scanning for weaknesses and opportunities. He despises authority but is smart enough to feign obedience to Captain Thorne.",
    voice="JBFqnCBsd6RMkjVDRZzb",
    race_preferences={
        Race.HALF_ORC.value: 1,
        Race.TIEFLING.value: 1
    },
    class_preferences={
        "Rogue": 2,
        "Warlock": 1,
        "Paladin": -3
    },
    gender_preferences={},
    size_preferences={}
  ),
  CharacterCreate(
    user_id=1,
    world_id=1,
    name="Lady Seraphina Valerius",
    avatar=None,
    race=Race.HUMAN.value,
    size=Size.MEDIUM.value,
    alignment=Alignment.LAWFUL_EVIL.value,
    gender=Gender.FEMALE.value,
    profession="Merchant",
    background="A mysterious and elegant woman traveling to Waterdeep. She claims to be a merchant dealing in rare textiles, but her sharp eyes and guarded demeanor suggest there is more to her than she lets on. She keeps to her cabin and rarely interacts with the crew.",
    communication_style="Polite, eloquent, and condescending. She speaks with the refined accent of the nobility and treats the crew as mere servants. She makes a point of not using any nautical terms, highlighting her detachment from the world of the ship.",
    motivation="Her true motives are unknown. She is watchful and observant, taking note of everything that happens on the ship. She might be a rival agent, a spy, or something else entirely.",
    personality="Aloof, intelligent, and manipulative. She exudes an aura of superiority and entitlement. She is patient and calculating, never revealing her true intentions.",
    voice="JBFqnCBsd6RMkjVDRZzb",
    race_preferences={
        Race.HUMAN.value: 3
    },
    class_preferences={
        "Wizard": 2,
        "Bard": 1,
        "Barbarian": -3
    },
    gender_preferences={},
    size_preferences={}
  )
]
