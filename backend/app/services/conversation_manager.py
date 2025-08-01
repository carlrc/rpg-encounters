from typing import List
from pydantic_ai.messages import ModelMessage, ModelRequest, ModelResponse, TextPart


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
