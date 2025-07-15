from app.models.character import Character
from pydantic_ai import Agent, RunContext, TextOutput
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider
from app.models.memory import Memory
from pydantic_ai.messages import ModelMessage
from pydantic_ai.agent import AgentRunResult

MAX_MESSAGE_HISTORY = 8

class CharacterAgent:
    def __init__(self, character: Character):
        self.character = character
        self.agent = Agent(
            OpenAIModel(model_name='mistral', provider=OpenAIProvider(base_url='http://localhost:11434/v1')), 
            deps_type=list[str],
            system_prompt="You are a character in an RPG world. Consider your characteristics and memories in your reply. Keep your replies very short. Do not reference your characteristics in your reply. Do not give up your memories unless prompted.",
            instructions=character.to_prompt(),
            history_processors=[self._keep_recent_messages])
        self.run_result: AgentRunResult[str] = None
        
        @self.agent.instructions
        def add_memories(ctx: RunContext[list[str]]) -> str:  
            return f"MEMORIES={''.join(str(memory) for memory in ctx.deps)}"
        
    async def chat(self, player_transcript: str, memories: list[str]) -> AgentRunResult[str]:
        message_history = self.run_result.all_messages() if self.run_result else []
        self.run_result = await self.agent.run(player_transcript, deps=memories, message_history=message_history)
        return self.run_result
    
    async def _keep_recent_messages(self, messages: list[ModelMessage]) -> list[ModelMessage]:
        """Keep only the last N messages to manage token usage."""
        return messages[-MAX_MESSAGE_HISTORY:] if len(messages) > MAX_MESSAGE_HISTORY else messages
