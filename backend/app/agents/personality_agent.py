import logging

from pydantic_ai import Agent, UnexpectedModelBehavior
from pydantic_ai.models.openai import OpenAIModel

from app.agents.base_agent import MAX_RETRIES
from app.models.character import CharacterCreate

logger = logging.getLogger(__name__)


class PersonalityGenerator:
    @staticmethod
    async def generate_personality(character_data: CharacterCreate) -> str:
        """Generate personality profile from character attributes"""

        agent = Agent(
            OpenAIModel(model_name="gpt-4o"),
            system_prompt="""You are an expert at analyzing D&D characters and creating personality profiles for social interactions.
            Generate concise personality profiles (2-3 short sentences) that describe:
            1. Their social interaction style and preferences
            2. What behaviors/topics they appreciate (builds influence)
            3. What behaviors/topics they dislike (loses influence)
            4. How their background influences their social reactions
            5. Their sense of humor and storytelling preferences
            6. How their bias preferences (race, class, gender, etc.) affect their influence evaluation (keep short)
            IMPORTANT: Include specific mentions of their bias preferences and explain WHY they have these biases based on their background, profession, and experiences. Describe how these biases manifest in their trust interpretations.
            Format as a single paragraph suitable for AI influence evaluation. Focus on what would make this character trust or distrust someone in conversation, including their inherent biases.""",
            retries=MAX_RETRIES,
        )

        prompt = f"""
            Analyze this D&D character and generate a personality profile for live interactions:
            Name: {character_data.name}
            Race: {character_data.race}
            Profession: {character_data.profession}
            Alignment: {character_data.alignment}
            Background: {character_data.background}
            Communication Style: {character_data.communication_style}
            Motivation: {character_data.motivation}
            Bias Preferences:
            Race Preferences: {character_data.race_preferences or 'None specified'}
            Class Preferences: {character_data.class_preferences or 'None specified'}
            Gender Preferences: {character_data.gender_preferences or 'None specified'}
            Size Preferences: {character_data.size_preferences or 'None specified'}
            IMPORTANT: Explain WHY this character has these specific bias preferences based on their background and experiences, and how these biases affect their trust evaluation of different types of people.
        """

        try:
            result = await agent.run(prompt)
            return result.output.strip()

        except UnexpectedModelBehavior as e:
            logger.error(f"Agent failure. {e.message}")
            raise
        except Exception as e:
            logger.error(f"Agent response generation failed. {e}")
            raise
