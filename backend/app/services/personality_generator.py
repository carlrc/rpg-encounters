from dotenv import load_dotenv
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel
from app.models.character import CharacterCreate

load_dotenv()

class PersonalityGenerator:
    @staticmethod
    async def generate_personality(character_data: CharacterCreate) -> str:
        """Generate personality profile from character attributes using Pydantic AI"""
        
        # Create Pydantic AI agent for personality generation
        agent = Agent(
            OpenAIModel(model_name='gpt-4o'),
            system_prompt="""You are an expert at analyzing D&D characters and creating personality profiles for social interactions.
            
            Generate concise personality profiles (2-3 sentences) that describe:
            1. Their social interaction style and preferences
            2. What behaviors/topics they appreciate (builds trust)
            3. What behaviors/topics they dislike (loses trust)
            4. How their background influences their social reactions
            5. Their sense of humor and storytelling preferences
            
            Format as a single paragraph suitable for AI trust evaluation. Focus on what would make this character trust or distrust someone in conversation."""
        )
        
        prompt = f"""
        Analyze this D&D character and generate a personality profile for social trust interactions:
        
        Name: {character_data.name}
        Race: {character_data.race}
        Profession: {character_data.profession}
        Alignment: {character_data.alignment}
        Background: {character_data.background}
        Communication Style: {character_data.communication_style}
        Motivation: {character_data.motivation}
        """
        
        try:
            result = await agent.run(prompt)
            return result.data.strip()
            
        except Exception as e:
            # Fallback personality based on basic attributes
            fallback = f"A {character_data.alignment.lower()} {character_data.race.lower()} {character_data.profession.lower()} who values {character_data.motivation.lower()}. Appreciates respectful conversation and behavior that aligns with their professional and moral values. Responds well to genuine interest in their work and background."
            return fallback
