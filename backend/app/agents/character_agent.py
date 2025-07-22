from typing import Any
from dotenv import load_dotenv
from app.models.character import Character
from pydantic_ai import Agent, NativeOutput, RunContext
from pydantic_ai.models.openai import OpenAIModel
from pydantic import BaseModel
from pydantic_ai.messages import ModelMessage
from pydantic_ai.agent import AgentRunResult
from app.models.player import Player
from app.models.trust import TRUST_CHANGE_MIN, TRUST_CHANGE_MAX, EARNED_TRUST_MIN, EARNED_TRUST_MAX, TrustState
from app.models.nugget import NuggetLevelInfo

MAX_MESSAGE_HISTORY = 10

class CharacterAgentOutput(BaseModel):
    response: str
    trust_level_adjustment: float
    trust_level_adjustment_reason: str

class CharacterAgent:
    def __init__(self, character: Character, player: Player, system_prompt: str, trust_state: TrustState):
        load_dotenv()
        self.character = character
        self.player = player
        self.trust = trust_state
                
        # Build trust-aware instructions
        trust_instruction = self._build_trust_instruction(character, player, trust_state)
        
        agent = Agent(
            OpenAIModel(model_name='gpt-4o'), 
            system_prompt=system_prompt + "\n" + character.to_prompt(),
            instructions=trust_instruction,
            history_processors=[self._keep_recent_messages],
            output_type=NativeOutput(CharacterAgentOutput,description='Return the chat response along with the trust adjustment and accompanying reason.'))
        self.run_result: AgentRunResult[CharacterAgentOutput] = None
        
        # Decorator does not work on self.agent
        @agent.instructions
        def add_nuggets(ctx: RunContext[list[NuggetLevelInfo]]) -> str:  
            available_nuggets = [nugget for nugget in ctx.deps if nugget.available]
            conditional_nuggets = [nugget for nugget in ctx.deps if nugget.conditionally_available]
            
            instruction_parts = []
            
            # Available secrets section
            if available_nuggets:
                nuggets_with_level = '\n'.join(f"- [{nugget.level}] {nugget.content}" for nugget in available_nuggets)
                instruction_parts.append(f"""# Available Secrets {nuggets_with_level}""")
            else:
                instruction_parts.append("# Available Secrets\nNo secrets are currently available.")
            
            # Conditional secrets section
            if conditional_nuggets:
                current_trust = self.trust.total_trust
                conditional_list = []
                for nugget in conditional_nuggets:
                    trust_needed = nugget.trust_needed - current_trust
                    conditional_list.append(f"- [{nugget.level}] {nugget.content}\n  → Available if you give +{trust_needed:.2f} or more trust (current: {current_trust:.2f}, need: {nugget.trust_needed:.2f})")
                
                conditional_text = '\n'.join(conditional_list)
                instruction_parts.append(f"""# Conditionally Available Secrets (unlock with trust adjustment)
                    {conditional_text}
                    **CONDITIONAL USAGE**: You can use conditional secrets if your trust adjustment would unlock them.""")
            
            instruction_parts.append("**PRIORITY**: Use EXCLUSIVE secrets first, then PRIVILEGED, then PUBLIC. Only reveal one secret per response.")
            
            return '\n\n'.join(instruction_parts)
        
        @agent.output_validator
        def validate_trust_adjustment(ctx: RunContext[Any], output: CharacterAgentOutput) -> CharacterAgentOutput:
            # Clamp trust adjustment to valid range
            output.trust_level_adjustment = max(TRUST_CHANGE_MIN, min(TRUST_CHANGE_MAX, output.trust_level_adjustment))
            # Updated earned trust
            self.trust.earned_trust += output.trust_level_adjustment
            
            return output
                
        # Set instance variable after decorators defined
        self.agent = agent
        
    async def chat(self, player_transcript: str, nugget_levels: list[NuggetLevelInfo]):
        message_history = self.run_result.all_messages() if self.run_result else None
        self.run_result = await self.agent.run(player_transcript, deps=nugget_levels, message_history=message_history)
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
        
        base_instruction = f"""## Current Interaction Context
            You are speaking with **{player.name}**: a {player.race} {player.gender} {player.class_name} who looks like {player.appearance}."""

        if not has_trust_preferences:
            return f"""{base_instruction}
                **INTERACTION MODE**: BASIC - No trust system configured. Keep responses shallow and surface-level."""
        
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
