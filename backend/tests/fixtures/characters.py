from app.models.character import CharacterCreate, CommunicationStyle
from app.models.race import Race, Size, Gender
from app.models.alignment import Alignment

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
    communication_style_type=CommunicationStyle.PROFANE.value,
    background="Born into a minor noble family that lost its fortune, Elias Thorne turned to the sea to reclaim his family's honor and wealth. He is a stern and pragmatic leader, respected and feared by his crew. He runs a tight ship and has no tolerance for nonsense.",
    motivation="To restore his family's name and fortune, and to prove his worth as a captain and a nobleman. He is secretly transporting a valuable and ancient artifact to a wealthy collector in Waterdeep.",
    voice="froLDspwCiytX4g1Pobg",
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
    communication_style_type=CommunicationStyle.PARANOID.value,
    background="A former city guard from a rough district, Barthus is as strong as an ox and twice as stubborn. He values order and discipline above all else. He's fiercely loyal to Captain Thorne, who gave him a respectable job after he was dismissed from the guard for excessive force.",
    motivation="To maintain order on the ship and protect the cargo at all costs. His loyalty to the captain is absolute, and he sees the ship's success as his own.",
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
    communication_style_type=CommunicationStyle.JOKING.value,
    background="An old sailor who has spent more of his life on the sea than on land. He's seen it all and is deeply superstitious. He's responsible for the general maintenance of the ship and its equipment.",
    motivation="To earn enough coin to retire comfortably in a quiet port town. He's not above a bit of smuggling on the side if the opportunity arises.",
    voice="7kBsLPSomsBitGHuwCdF",
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
    communication_style_type=CommunicationStyle.CUSTOM.value,
    background="A young man from a poor fishing village, trying to make a name for himself. He is agile and quick, known for his skill in climbing the rigging.",
    communication_style="Speaks with a thick, rural accent, often mumbling. He uses simple, un-nautical language unless repeating an order. He says 'aye' and 'right' a lot. He's not confident enough to engage in the typical sailor banter.",
    motivation="To see the world beyond his small village and perhaps find his fortune. He is impressionable and eager to prove his worth.",
    personality="Hardworking and diligent, but a bit naive. He is easily intimidated by the older crew members and is wary of strangers.",
    voice="HYM6YgFANZinEBanknZK",
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
    communication_style_type=CommunicationStyle.FLIRTATIOUS.value,
    background="Mara has worked on ships most of her life, following her father who was also a cook. She is tough and no-nonsense, but has a kind heart buried under a gruff exterior. The galley is her kingdom, and she rules it with an iron ladle.",
    motivation="To provide good, hearty meals for the crew and ensure everyone is well-fed and healthy. She feels a sense of responsibility for the crew's well-being.",
    voice="FVQMzxJGPUBtfz1Azdoy",
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
    communication_style_type=CommunicationStyle.NERDY.value,
    background="A former pirate who lost an eye in a raid. He managed to escape the noose and now works on merchant ships, biding his time. He is cruel and enjoys the suffering of others.",
    motivation="Greed and self-preservation. He is always looking for an angle to exploit for personal gain and is not loyal to anyone but himself.",
    voice="2EVscXwJhGYuLiX1PgKA",
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
    communication_style_type=CommunicationStyle.THEATRICAL.value,
    background="A mysterious and elegant woman traveling to Waterdeep. She claims to be a merchant dealing in rare textiles, but her sharp eyes and guarded demeanor suggest there is more to her than she lets on. She keeps to her cabin and rarely interacts with the crew.",
    motivation="Her true motives are unknown. She is watchful and observant, taking note of everything that happens on the ship. She might be a rival agent, a spy, or something else entirely.",
    voice="CAm8Nf1Krs1nSXtbaMmI",
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
