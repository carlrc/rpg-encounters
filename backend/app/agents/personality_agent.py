import logging

from langfuse import get_client, observe
from pydantic_ai import UnexpectedModelBehavior

from app.agents.base_agent import BaseAgent
from app.agents.prompts.import_prompts import render_prompt
from app.models.character import CharacterCreate

logger = logging.getLogger(__name__)


class PersonalityAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        self.agent = self._generate_agent()

    @observe(capture_input=False, capture_output=False)
    async def generate(self, character: CharacterCreate) -> str:
        """Generate personality profile from character attributes"""
        try:
            # Render the Jinja template with character data
            rendered_prompt = render_prompt(
                "personality_agent", {"character": character}
            )

            run_result = await self.agent.run(rendered_prompt)

            get_client().update_current_trace(
                name="personality-agent", metadata=self.metadata
            )

            return run_result.output.strip()

        except UnexpectedModelBehavior as e:
            logger.error(f"Agent failure. {e.message}")
            raise
        except Exception as e:
            logger.error(f"Agent response generation failed. {e}")
            raise
