from enum import Enum
import logging
from typing import Dict, List
from app.models.class_traits import VALID_SKILLS
from app.models.player import Player
from app.models.reveal import Reveal, RevealLayer

logger = logging.getLogger(__name__)


class D20Outcomes(Enum):
    CRITICAL_SUCCESS = 20
    CRITICAL_FAILURE = 1


def get_skill_bonus(skill: str, player_skills: Dict[str, int]) -> int:
    """
    Validate skill parameter and return skill bonus.
    """
    if skill not in VALID_SKILLS:
        raise ValueError(f"Invalid skill '{skill}'. Valid skills: {VALID_SKILLS}")

    if skill not in player_skills:
        raise ValueError(
            f"Player does not have skill '{skill}'. Player skills: {list(player_skills.keys())}"
        )

    return player_skills[skill]


def calculate_skill_check(skill: str, player: Player, d20_roll: int) -> int:
    """
    Calculate a skill check: d20 + skill bonus.
    """
    skill_bonus = get_skill_bonus(skill, player.skills)
    total = d20_roll + skill_bonus

    logger.info(
        f"Skill check for {player.name}: {skill} - d20: {d20_roll}, skill bonus: {skill_bonus}, total: {total}"
    )
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
