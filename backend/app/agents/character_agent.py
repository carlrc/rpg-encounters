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
            return f"""# Trust Nuggets
            These are {self.character.name} trust-based secrets.

            ## Available Secrets
                {nuggets_list}
            """
        
        # Set instance variable after decorators defined
        self.agent = agent
        
    async def chat(self, player_transcript: str, available_nuggets: list[str], unavailable_nuggets: list[str]) -> AgentRunResult[str]:
        message_history = self.run_result.all_messages() if self.run_result else None
        self.run_result = await self.agent.run(player_transcript, deps=available_nuggets, message_history=message_history)
        return self.run_result
    
    def _build_trust_instruction(self, character: Character, player: Player, trust_state) -> str:
        """Build trust-aware instruction for the AI"""
        # Check if character has trust preferences configured
        has_trust_preferences = (
            character.race_preferences or 
            character.class_preferences or 
            character.gender_preferences or 
            character.size_preferences or
            character.appearance_keywords or
            character.storytelling_keywords
        )
        
        if not has_trust_preferences:
            # TODO: Make entry and exit shallow conversations
            # No trust system configured - shallow interaction only
            return f"""{character.to_prompt()}

You are speaking with a {player.race} {player.gender} {player.class_name} who looks like {player.appearance}.

INTERACTION MODE: BASIC
You have no special secrets or trust system configured. Keep your responses shallow and surface-level. You are polite but don't share anything particularly interesting or personal. Respond naturally as {character.name} but without revealing any deep information about yourself or others."""
        
        # Trust system is configured - full trust evaluation
        # Calculate trust ranges for display
        current_earned = trust_state.earned_trust
        min_earned = max(EARNED_TRUST_MIN, current_earned + TRUST_CHANGE_MIN)
        max_earned = min(EARNED_TRUST_MAX, current_earned + TRUST_CHANGE_MAX)
        
        # Build personality description from character fields
        personality_parts = []
        if character.background:
            personality_parts.append(f"Background: {character.background}")
        if character.communication_style:
            personality_parts.append(f"Communication Style: {character.communication_style}")
        if character.motivation:
            personality_parts.append(f"Motivation: {character.motivation}")
        
        personality = "\n".join(personality_parts) if personality_parts else "No detailed personality configured."
        
        instruction = f"""{character.to_prompt()}

You are speaking with a {player.race} {player.gender} {player.class_name} who looks like {player.appearance}.

PERSONALITY FOR TRUST EVALUATION:
{personality}

CURRENT TRUST STATUS:
- Base Trust: {trust_state.base_trust:.2f} (from player characteristics)
- Earned Trust: {trust_state.earned_trust:.2f} (from interactions)
- Total Trust: {trust_state.total_trust:.2f}

TRUST EVALUATION:
Based on your personality above, evaluate this player's message:
1. Does it align with what you appreciate?
2. Does it show understanding of who you are?
3. Is the social approach appropriate for your character?
4. Does it contain good storytelling, appropriate humor, or meaningful connection?
5. Does it go against your values or show disrespect?

TRUST ADJUSTMENT:
Adjust earned trust by {TRUST_CHANGE_MIN} to {TRUST_CHANGE_MAX} based on this evaluation.
Current earned trust range: {min_earned:.1f} to {max_earned:.1f}

INSTRUCTIONS:
1. Evaluate the message based on your personality
2. Decide earned trust change ({TRUST_CHANGE_MIN} to {TRUST_CHANGE_MAX})
3. Calculate your new total trust level
4. Use the available secrets provided to you through the nuggets system
5. Respond naturally as {character.name}

You handle all trust calculations and secret revealing - no system will process your response."""
        
        return instruction

    async def _keep_recent_messages(self, messages: list[ModelMessage]) -> list[ModelMessage]:
        """Keep only the last N messages to manage token usage."""
        return messages[-MAX_MESSAGE_HISTORY:] if len(messages) > MAX_MESSAGE_HISTORY else messages
