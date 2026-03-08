import logging
from typing import Tuple

from app.agents.agent_output import ConversationAgentOutput
from app.models.reveal import REVEAL_DEFAULT_THRESHOLDS, Reveal, RevealLayer

logger = logging.getLogger(__name__)


def select_response(
    reveals: list[Reveal],
    agent_result: ConversationAgentOutput,
    influence_score: int,
) -> Tuple[str, RevealLayer]:

    negative_attitude = (
        influence_score < REVEAL_DEFAULT_THRESHOLDS[RevealLayer.STANDARD]
    )
    # Handle response attitude given no reveals or no referenced reveal
    if not reveals or agent_result.reveal_id is None:
        if negative_attitude:
            return agent_result.negative_response, RevealLayer.NEGATIVE
        else:
            return agent_result.standard_response, RevealLayer.STANDARD

    # If reveals are assigned to this character find what the LLM returned
    selected_reveal = None
    for reveal in reveals:
        if reveal.id == agent_result.reveal_id:
            selected_reveal = reveal
            break

    # If the LLM returns an invalid reveal_id or stringified None, default to the standard response
    if selected_reveal is None:
        # Often if the LLM doesn't reference a reveal it will return "None", so we use standard assuming it doesn't contain sensitive information
        logger.warning(
            f"reveal_id {agent_result.reveal_id} not found in available list. Defaulting to standard answer..."
        )
        return agent_result.standard_response, RevealLayer.STANDARD
    else:
        # Given a valid reveal, select response in desc order based on influence levels and reveal-specific thresholds
        if negative_attitude:
            return agent_result.negative_response, RevealLayer.NEGATIVE
        elif (
            agent_result.exclusive_response
            and influence_score >= selected_reveal.get_threshold(RevealLayer.EXCLUSIVE)
        ):
            return agent_result.exclusive_response, RevealLayer.EXCLUSIVE
        elif (
            agent_result.privileged_response
            and influence_score >= selected_reveal.get_threshold(RevealLayer.PRIVILEGED)
        ):
            return agent_result.privileged_response, RevealLayer.PRIVILEGED
        else:
            return agent_result.standard_response, RevealLayer.STANDARD
