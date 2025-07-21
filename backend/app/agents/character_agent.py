from dotenv import load_dotenv
from app.models.character import Character
from pydantic_ai import Agent, RunContext
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.messages import ModelMessage
from pydantic_ai.agent import AgentRunResult
from app.models.player import Player
from app.models.nugget import NuggetLayer
from app.services.nugget_service import NuggetService
from app.models.trust import TRUST_CHANGE_MIN, TRUST_CHANGE_MAX, EARNED_TRUST_MIN, EARNED_TRUST_MAX
from app.data.trust_store import trust_state_store
from app.services.trust_calculator import TrustCalculator

MAX_MESSAGE_HISTORY = 10

class CharacterAgent:
    def __init__(self, character: Character, player: Player, system_prompt: str):
        load_dotenv()
        self.character = character
        self.player = player
        
        # Get current trust state (should already exist from previous interactions)
        trust_state = trust_state_store.get_trust_state(character.id, player.id)
        if not trust_state:
            # If no trust state exists, create one with calculated base trust
            base_trust = TrustCalculator.calculate_base_trust(character, player)
            trust_state = trust_state_store.get_or_create(character.id, player.id, base_trust)
        
        # Build trust-aware instructions
        trust_instruction = self._build_trust_instruction(character, player, trust_state)
        
        agent = Agent(
            OpenAIModel(model_name='gpt-4o'), 
            deps_type=list[str],
            system_prompt=system_prompt,
            instructions=trust_instruction,
            history_processors=[self._keep_recent_messages])
        self.run_result: AgentRunResult[str] = None
        
        # Decorator does not work on self.agent
        @agent.instructions
        def add_nuggets(ctx: RunContext[list[str]]) -> str:  
            nuggets_list = '\n'.join(f"- {nugget}" for nugget in ctx.deps)
            return f"""# Available Secrets
                {nuggets_list}
                **PRIORITY**: Use EXCLUSIVE secrets first, then PRIVILEGED, then PUBLIC. Only reveal one secret per response."""
        
        # Set instance variable after decorators defined
        self.agent = agent
        
    async def chat(self, player_transcript: str, available_nuggets: list[str], unavailable_nuggets: list[str]) -> AgentRunResult[str]:
        message_history = self.run_result.all_messages() if self.run_result else None
        self.run_result = await self.agent.run(player_transcript, deps=available_nuggets, message_history=message_history)
        return self.run_result
    
    def _build_trust_instruction(self, character: Character, player: Player, trust_state) -> str:
        """Build streamlined trust-aware instruction for the AI"""
        # Check if character has trust preferences configured
        has_trust_preferences = (
            character.race_preferences or 
            character.class_preferences or 
            character.gender_preferences or 
            character.size_preferences or
            character.appearance_keywords or
            character.storytelling_keywords
        )
        
        base_instruction = f"""{character.to_prompt()}

## Current Interaction Context

You are speaking with **{player.name}**: a {player.race} {player.gender} {player.class_name} who looks like {player.appearance}."""

        if not has_trust_preferences:
            return f"""{base_instruction}

**INTERACTION MODE**: BASIC - No trust system configured. Keep responses shallow and surface-level without revealing deep secrets."""
        
        # Trust system is configured - add trust status
        current_earned = trust_state.earned_trust
        min_earned = max(EARNED_TRUST_MIN, current_earned + TRUST_CHANGE_MIN)
        max_earned = min(EARNED_TRUST_MAX, current_earned + TRUST_CHANGE_MAX)
        
        return f"""{base_instruction}

## Trust Status
- **Base Trust**: {trust_state.base_trust:.2f} (from player characteristics)
- **Earned Trust**: {trust_state.earned_trust:.2f} (from interactions so far)  
- **Total Trust**: {trust_state.total_trust:.2f}

## Trust Adjustment Range
Adjust earned trust by {TRUST_CHANGE_MIN} to {TRUST_CHANGE_MAX} based on message evaluation.
New earned trust range: {min_earned:.1f} to {max_earned:.1f}

**PROCESS**: Evaluate message → Adjust trust → Use appropriate secrets → Respond naturally"""

    async def _keep_recent_messages(self, messages: list[ModelMessage]) -> list[ModelMessage]:
        """Keep only the last N messages to manage token usage."""
        return messages[-MAX_MESSAGE_HISTORY:] if len(messages) > MAX_MESSAGE_HISTORY else messages
