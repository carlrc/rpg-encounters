from app.models.character import Character
from app.models.influence import BASE_INFLUENCE_MAX, BASE_INFLUENCE_MIN
from app.models.player import Player


def calculate_base_influence(character: Character, player: Player) -> int:
    """Calculate starting influence from player characteristics (DC scale 0-15)"""
    influence = 0

    # Add race preference modifier
    if character.race_preferences:
        influence += character.race_preferences.get(player.race, 0)

    # Add class preference modifier
    if character.class_preferences:
        influence += character.class_preferences.get(player.class_name, 0)

    # Add gender preference modifier
    if character.gender_preferences:
        influence += character.gender_preferences.get(player.gender, 0)

    # Add size preference modifier
    if character.size_preferences:
        influence += character.size_preferences.get(player.size, 0)

    return max(BASE_INFLUENCE_MIN, min(BASE_INFLUENCE_MAX, influence))
