import logging
from typing import List, Tuple

from pydantic_ai.messages import ModelMessage, ModelRequest, ModelResponse, TextPart

from app.agents.agent_output import ConversationAgentOutput
from app.models.reveal import REVEAL_DEFAULT_THRESHOLDS, Reveal, RevealLayer

logger = logging.getLogger(__name__)


class ConversationManager:
    def __init__(self):
        self.messages: List[ModelMessage] = []

    def add_user_message(self, message: ModelRequest) -> None:
        """Add user message to conversation history"""
        self.messages.append(message)

    def add_agent_response(self, response: str) -> None:
        """Add agent response to conversation history"""
        message = ModelResponse(parts=[TextPart(content=response)])

        self.messages.append(message)

    def get_history(self) -> List[ModelMessage]:
        """Get conversation history for agent runs"""
        return self.messages.copy()

    def select_response(
        self,
        reveals: list[Reveal],
        agent_result: ConversationAgentOutput,
        total_trust: int,
    ) -> Tuple[str, RevealLayer]:
        # Handle response attitude given no reveals
        negative_attitude = (
            total_trust < REVEAL_DEFAULT_THRESHOLDS[RevealLayer.STANDARD]
        )
        if not reveals:
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
            logger.debug(
                f"reveal_id {agent_result.reveal_id} not found in available list. Defaulting to standard answer..."
            )
            return agent_result.standard_response, RevealLayer.STANDARD
        else:
            # Select response in desc order based on trust levels and reveal-specific thresholds
            if negative_attitude:
                return agent_result.negative_response, RevealLayer.NEGATIVE
            elif (
                agent_result.exclusive_response
                and total_trust >= selected_reveal.get_threshold(RevealLayer.EXCLUSIVE)
            ):
                return agent_result.exclusive_response, RevealLayer.EXCLUSIVE
            elif (
                agent_result.privileged_response
                and total_trust >= selected_reveal.get_threshold(RevealLayer.PRIVILEGED)
            ):
                return agent_result.privileged_response, RevealLayer.PRIVILEGED
            else:
                return agent_result.standard_response, RevealLayer.STANDARD
