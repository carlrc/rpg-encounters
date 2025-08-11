from app.models.character import Character
from app.models.player import Player
from app.models.trust import BASE_TRUST_MIN, BASE_TRUST_MAX


def calculate_base_trust(character: Character, player: Player) -> int:
    """Calculate starting trust from player characteristics (DC scale 0-15)"""
    trust = 0

    # Race preference
    if character.race_preferences:
        trust += character.race_preferences.get(player.race, 0)

    # Class preference
    if character.class_preferences:
        trust += character.class_preferences.get(player.class_name, 0)

    # Gender preference
    if character.gender_preferences:
        trust += character.gender_preferences.get(player.gender, 0)

    # Size preference
    if character.size_preferences:
        trust += character.size_preferences.get(player.size, 0)

    return max(BASE_TRUST_MIN, min(BASE_TRUST_MAX, trust))
