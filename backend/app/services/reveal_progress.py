"""Service for calculating reveal progress based on influence scores."""

from typing import Dict

from app.models.reveal import Reveal


def calculate_reveal_progress(reveal: Reveal, influence_score: int) -> Dict:
    """
    Calculate how many reveal layers are unlocked based on influence score.
    """
    unlocked_layers = 0

    # Check each threshold
    if influence_score >= reveal.standard_threshold:
        unlocked_layers += 1
    if influence_score >= reveal.privileged_threshold:
        unlocked_layers += 1
    if influence_score >= reveal.exclusive_threshold:
        unlocked_layers += 1

    # Count total layers (only count non-None content)
    total_layers = 0
    if reveal.level_1_content:
        total_layers += 1
    if reveal.level_2_content:
        total_layers += 1
    if reveal.level_3_content:
        total_layers += 1

    return {
        "id": reveal.id,
        "title": reveal.title,
        "progress": f"{unlocked_layers}/{total_layers}",
        "unlocked_layers": unlocked_layers,
        "total_layers": total_layers,
    }
