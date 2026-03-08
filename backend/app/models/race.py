from enum import Enum


class Race(Enum):
    HUMAN = "Human"
    HILL_DWARF = "Hill Dwarf"
    MOUNTAIN_DWARF = "Mountain Dwarf"
    HIGH_ELF = "High Elf"
    WOOD_ELF = "Wood Elf"
    LIGHTFOOT_HALFLING = "Lightfoot Halfling"
    STOUT_HALFLING = "Stout Halfling"
    DRAGONBORN = "Dragonborn"
    FOREST_GNOME = "Forest Gnome"
    ROCK_GNOME = "Rock Gnome"
    HALF_ELF = "Half-Elf"
    HALF_ORC = "Half-Orc"
    TIEFLING = "Tiefling"


class Size(Enum):
    SMALL = "Small"
    MEDIUM = "Medium"
    LARGE = "Large"


class Gender(Enum):
    MALE = "male"
    FEMALE = "female"
    NONBINARY = "nonbinary"


VALID_RACES = [race.value for race in Race]
VALID_SIZES = [size.value for size in Size]
VALID_GENDERS = [gender.value for gender in Gender]
