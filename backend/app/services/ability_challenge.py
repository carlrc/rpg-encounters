import logging
from enum import Enum
from typing import List

from app.models.class_traits import Abilities
from app.models.influence import Influence
from app.models.player import Player
from app.models.reveal import Reveal, RevealLayer

logger = logging.getLogger(__name__)


class D20Outcomes(Enum):
    CRITICAL_SUCCESS = 20
    CRITICAL_FAILURE = 1


def calculate_skill_check(
    skill: str, player: Player, influence: Influence, d20_roll: int
) -> int:
    """
    Calculate a skill check: d20 + modifiers.
    """
    skill_modifier = player.skills.get(skill, 0)
    charisma_modifier = player.abilities.get(Abilities.CHARISMA.value, 0)
    # NOTE: Adding positive influence makes the final scores too high, so only include if negative (e.g., character dislikes them)
    negative_influence_modifier = influence.score if influence.score <= 0 else 0

    total = d20_roll + charisma_modifier + skill_modifier + negative_influence_modifier

    return total


def filter_reveals_by_roll(reveals: List[Reveal], total_roll: int) -> List[str]:
    """
    Filter all reveals based on skill check total.
    """
    filtered_reveals = []

    for reveal in reveals:
        # Check reveals in desc priority
        # We don't want to confuse the LLM will multiple versions of the same information

        exclusive_threshold = reveal.get_threshold(RevealLayer.EXCLUSIVE)
        if total_roll >= exclusive_threshold and reveal.level_3_content:
            filtered_reveals.append(reveal.level_3_content)
            continue

        privileged_threshold = reveal.get_threshold(RevealLayer.PRIVILEGED)
        if total_roll >= privileged_threshold and reveal.level_2_content:
            filtered_reveals.append(reveal.level_2_content)
            continue

        standard_threshold = reveal.get_threshold(RevealLayer.STANDARD)
        if total_roll >= standard_threshold and reveal.level_1_content:
            filtered_reveals.append(reveal.level_1_content)

    return filtered_reveals
