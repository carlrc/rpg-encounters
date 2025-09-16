from app.models.player import PlayerCreate
from app.models.race import Race, Size, Gender
from app.models.alignment import Alignment
from app.models.class_traits import Abilities, Class, Skills

players_db = [
    PlayerCreate(
        user_id=1,
        world_id=1,
        name="Mira Underbough",
        rl_name="Sarah Johnson",
        appearance="Small lightfoot halfling with tan skin, jaw-length dark curls, hazel eyes, and a scuffed hooded leather cloak. Fitted leathers with a slim belt, silvered dagger, and small stitched pouches.",
        race=Race.LIGHTFOOT_HALFLING.value,
        class_name=Class.ROGUE.value,
        size=Size.SMALL.value,
        alignment=Alignment.CHAOTIC_GOOD.value,
        gender=Gender.FEMALE.value,
        abilities={
            Abilities.CHARISMA.value: 3
        },
        skills={
            Skills.DECEPTION.value: 5,
            Skills.INTIMIDATION.value: 3,
            Skills.PERFORMANCE.value: 3,
            Skills.PERSUASION.value: 3
        }
    ),
    PlayerCreate(
        user_id=1,
        world_id=1,
        name="Sir Alaric Duskbane",
        rl_name="Michael Chen",
        appearance="Broad-shouldered human in clean chain mail and a sun-emblazoned tabard, with close-cropped dark hair and gray eyes. A thin jaw scar, square features, worn gauntlets, and a polished scabbard at the hip.",
        race=Race.HUMAN.value,
        class_name=Class.PALADIN.value,
        size=Size.MEDIUM.value,
        alignment=Alignment.LAWFUL_GOOD.value,
        gender=Gender.MALE.value,
        abilities={
            Abilities.CHARISMA.value: 2
        },
        skills={
            Skills.DECEPTION.value: 2,
            Skills.INTIMIDATION.value: 4,
            Skills.PERFORMANCE.value: 2,
            Skills.PERSUASION.value: 4
        }
    ),
    PlayerCreate(
        user_id=1,
        world_id=1,
        name="Thalion Oakenshade",
        rl_name="David Williams",
        appearance="Lean wood elf with pale-olive skin, high cheekbones, moss-green eyes, and ash-braided hair. Bark-hued cloak over fitted leathers; long limbs, faint bowstring marks, and a longbow with greatsword on a tidy harness.",
        race=Race.WOOD_ELF.value,
        class_name=Class.FIGHTER.value,
        size=Size.MEDIUM.value,
        alignment=Alignment.NEUTRAL_GOOD.value,
        gender=Gender.MALE.value,
        abilities={
            Abilities.CHARISMA.value: -1
        },
        skills={
            Skills.DECEPTION.value: -1,
            Skills.INTIMIDATION.value: -1,
            Skills.PERFORMANCE.value: -1,
            Skills.PERSUASION.value: -1
        }
    ),
    PlayerCreate(
        user_id=1,
        world_id=1,
        name="Brynja Stoneforge",
        rl_name="Emma Rodriguez",
        appearance="Stocky hill dwarf in soot-dusted chain mail with ruddy skin and braided auburn hair ringed in copper. An anvil-shaped holy symbol at the collar; thick, callused knuckles, and a belt with a compact hammer and satchel.",
        race=Race.HILL_DWARF.value,
        class_name=Class.CLERIC.value,
        size=Size.MEDIUM.value,
        alignment=Alignment.LAWFUL_GOOD.value,
        gender=Gender.FEMALE.value,
        abilities={
            Abilities.CHARISMA.value: 0
        },
        skills={
            Skills.DECEPTION.value: 1,
            Skills.INTIMIDATION.value: 3,
            Skills.PERFORMANCE.value: 1,
            Skills.PERSUASION.value: 1
        }
    ),
    PlayerCreate(
        user_id=1,
        world_id=1,
        name="Elaris Moonglade",
        rl_name="James Thompson",
        appearance="Slender high elf in deep-blue robes stitched with faint silver sigils, with pale skin, sharp features, and pale blue eyes. Ink-stained fingers, platinum-blond hair tied back, and a leather satchel of scroll tubes and lenses.",
        race=Race.HIGH_ELF.value,
        class_name=Class.WIZARD.value,
        size=Size.MEDIUM.value,
        alignment=Alignment.NEUTRAL_GOOD.value,
        gender=Gender.MALE.value,
        abilities={
            Abilities.CHARISMA.value: 1
        },
        skills={
            Skills.DECEPTION.value: -1,
            Skills.INTIMIDATION.value: -1,
            Skills.PERFORMANCE.value: -1,
            Skills.PERSUASION.value: -1
        }
    )
]
