from app.models.reveal import RevealLayer, Reveal


def select_response_by_trust(
    public_response: str,
    privileged_response: str | None,
    exclusive_response: str | None,
    total_trust: int,
    reveal: Reveal,
) -> tuple[str, RevealLayer]:
    """
    Select appropriate response based on trust levels and reveal-specific thresholds.

    Args:
        public_response: Public level response
        privileged_response: Privileged level response (optional)
        exclusive_response: Exclusive level response (optional)
        total_trust: Current total trust level (DC scale 0-30)
        reveal: The reveal being used (contains threshold info)

    Returns:
        Tuple of (selected_response, response_level)
    """
    # Select response based on trust levels and reveal-specific thresholds
    if exclusive_response and total_trust >= reveal.get_threshold(
        RevealLayer.EXCLUSIVE
    ):
        return exclusive_response, RevealLayer.EXCLUSIVE
    elif privileged_response and total_trust >= reveal.get_threshold(
        RevealLayer.PRIVILEGED
    ):
        return privileged_response, RevealLayer.PRIVILEGED
    else:
        return public_response, RevealLayer.PUBLIC
