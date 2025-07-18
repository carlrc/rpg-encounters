from dotenv import load_dotenv
from app.models.character import Character
from pydantic_ai import Agent, RunContext
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.messages import ModelMessage
from pydantic_ai.agent import AgentRunResult
from app.models.player import Player
from app.models.trust import NuggetLayer
from app.data.trust_store import trust_profile_store, nugget_store, trust_state_store
from app.services.trust_calculator import TrustCalculator

MAX_MESSAGE_HISTORY = 10

class CharacterAgent:
    def __init__(self, character: Character, player: Player, system_prompt: str):
        load_dotenv()
        self.character = character
        self.player = player
        
        # Get or create trust state with base trust calculation
        trust_state = trust_state_store.get_or_create(character.id, player.id)
        if trust_state.current_trust == 0.0:  # Only calculate base trust once
            trust_profile = trust_profile_store.get_by_character_id(character.id)
            if trust_profile:
                base_trust = TrustCalculator.calculate_base_trust(trust_profile, player)
                trust_state.current_trust = base_trust
                trust_state_store.update_trust_state(trust_state)
        
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
        def add_memories(ctx: RunContext[list[str]]) -> str:  
            memories_list = '\n'.join(f"- {memory}" for memory in ctx.deps)
            return f"""# Memories
            These are {self.character.name} memories.

            ## Summary
                {memories_list}
            """
        
        # Set instance variable after decorators defined
        self.agent = agent
        
    async def chat(self, player_transcript: str, memories: list[str]) -> AgentRunResult[str]:
        message_history = self.run_result.all_messages() if self.run_result else None
        self.run_result = await self.agent.run(player_transcript, deps=memories, message_history=message_history)
        return self.run_result
    
    def _build_trust_instruction(self, character: Character, player: Player, trust_state) -> str:
        """Build trust-aware instruction for the AI"""
        trust_profile = trust_profile_store.get_by_character_id(character.id)
        if not trust_profile:
            return f"{character.to_prompt()}. You are speaking with a {player.race} {player.gender} who looks like {player.appearance}."
        
        # Get all nuggets organized by layer
        all_nuggets = nugget_store.get_by_character_id(character.id)
        
        # Organize by layer
        public_nuggets = [n for n in all_nuggets if n.layer == NuggetLayer.PUBLIC]
        privileged_nuggets = [n for n in all_nuggets if n.layer == NuggetLayer.PRIVILEGED]
        exclusive_nuggets = [n for n in all_nuggets if n.layer == NuggetLayer.EXCLUSIVE]
        
        instruction = f"""{character.to_prompt()}

You are speaking with a {player.race} {player.gender} {player.class_name} who looks like {player.appearance}.

CURRENT TRUST LEVEL: {trust_state.current_trust:.2f}/1.0

TRUST & SECRET SYSTEM:
- Analyze this message for storytelling elements: {trust_profile.storytelling_keywords}
- If worthy elements found, add 0.3 to current trust
- Reveal secrets based on FINAL trust level:

AVAILABLE SECRETS:
Public (0.0+ trust): {[n.content for n in public_nuggets]}
Privileged (0.34+ trust): {[n.content for n in privileged_nuggets]}  
Exclusive (0.67+ trust): {[n.content for n in exclusive_nuggets]}

INSTRUCTIONS:
1. Decide if this message deserves +0.3 trust
2. Calculate your final trust level
3. Reveal ALL secrets your final trust level unlocks
4. Respond naturally as {character.name}

You handle everything - no system will process your response."""
        
        return instruction

    async def _keep_recent_messages(self, messages: list[ModelMessage]) -> list[ModelMessage]:
        """Keep only the last N messages to manage token usage."""
        return messages[-MAX_MESSAGE_HISTORY:] if len(messages) > MAX_MESSAGE_HISTORY else messages
