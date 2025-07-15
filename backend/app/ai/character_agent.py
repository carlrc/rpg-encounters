from backend.app.models.character import Character
from pydantic_ai import Agent, RunContext, TextOutput, AgentRunResult
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider
from backend.app.models.memory import Memory
from backend.app.services.memory_manager import MemoryManager
from pydantic_ai.messages import ModelMessage
from pydantic_ai.agent import AgentRunResult

class CharacterAgent:
    def __init__(self, character: Character, memory_manager: MemoryManager):
        self.character = character
        self.memory_manager = memory_manager
        self.agent = Agent(
            OpenAIModel(model_name='mistral', provider=OpenAIProvider(base_url='http://localhost:11434')), 
            output_type=TextOutput,
            deps_type=list[Memory],
            system_prompt="You are a character in an RPG world. Consider your characteristics and memories in your reply",
            instructions=character.to_prompt(),
            history_processors=[self._keep_recent_messages])
        self.run_result: AgentRunResult[str] = None
        
        # Util functions
        @self.agent.instructions
        def add_memories(ctx: RunContext[list[Memory]]) -> str:  
            return f"MEMORIES={"".join(ctx)}"
        
    def chat(self, player_transcript: str, memories: list[Memory]) -> str:
        self.run_result = self.agent.run_sync(player_transcript, deps=memories, message_history=self.run_result.all_messages())
        return self.run_result.output
    
    async def _keep_recent_messages(messages: list[ModelMessage]) -> list[ModelMessage]:
        """Keep only the last 5 messages to manage token usage."""
        return messages[-5:] if len(messages) > 5 else messages