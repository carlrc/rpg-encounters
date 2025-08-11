from typing import List, Tuple
from pydantic_ai.messages import ModelMessage, ModelRequest, ModelResponse, TextPart
from app.models.reveal import Reveal, RevealLayer
import logging
from app.services.reveal_service import select_response_by_trust
from app.agents.character_agent_output import CharacterAgentOutput

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
        agent_result: CharacterAgentOutput,
        total_trust: int,
    ) -> Tuple[str, RevealLayer]:
        # If there are no reveals assigned to the character default to public response
        if not reveals:
            return agent_result.public_response, RevealLayer.PUBLIC

        # If reveals are assigned to this character find what the LLM returned
        selected_reveal = None
        for reveal in reveals:
            if reveal.id == agent_result.reveal_id:
                selected_reveal = reveal
                break

        # If the LLM returns an invalid reveal_id, default to the public response and log the error
        if selected_reveal is None:
            # TODO: Could a error response be added to agent output (e.g., I'm sorry I can't talk right now) instead of defaulting to public
            logger.error(
                f"reveal_id {self.run_result.output.reveal_id} not found in available list"
            )
            return agent_result.public_response, RevealLayer.PUBLIC
        else:
            # If the reveal_id is found select the response based on earned trust
            return select_response_by_trust(
                public_response=agent_result.public_response,
                privileged_response=agent_result.privileged_response,
                exclusive_response=agent_result.exclusive_response,
                total_trust=total_trust,
                reveal=selected_reveal,
            )
