import logging
from typing import Union

from pydantic_ai import UnexpectedModelBehavior

from app.agents.base_agent import BaseAgent
from app.agents.prompts.import_prompts import render_prompt
from app.models.character import CharacterCreate, CharacterUpdate

logger = logging.getLogger(__name__)


class PersonalityAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        self.agent = self._generate_agent()

    async def generate(self, character: Union[CharacterCreate, CharacterUpdate]) -> str:
        """Generate personality profile from character attributes"""
        try:
            # Render the Jinja template with character data
            rendered_prompt = render_prompt(
                "personality_agent", {"character": character}
            )

            run_result = await self.agent.run(rendered_prompt)
            self.last_total_tokens = run_result.usage().total_tokens

            return run_result.output.strip()

        except UnexpectedModelBehavior as e:
            logger.error(f"Agent failure. {e.message}")
            raise
        except Exception as e:
            logger.error(f"Agent response generation failed. {e}")
            raise
