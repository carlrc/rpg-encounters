import ollama
import logging
from typing import AsyncGenerator, Optional

logger = logging.getLogger(__name__)

class OllamaService:
    def __init__(self, model_name: str = "mistral"):
        self.model_name = model_name
        self.client = ollama.AsyncClient()
        
    async def generate_response(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Generate a single response from the LLM"""
        try:
            messages = []
            
            if system_prompt:
                messages.append({
                    "role": "system",
                    "content": system_prompt
                })
            
            messages.append({
                "role": "user", 
                "content": prompt
            })
            
            response = await self.client.chat(
                model=self.model_name,
                messages=messages
            )
            
            return response['message']['content']
            
        except Exception as e:
            logger.error(f"Error generating LLM response: {e}")
            raise

    def get_dnd_character_system_prompt(self) -> str:
        """Get a system prompt for D&D character roleplay"""
        return """You are a D&D character in an interactive tabletop RPG session. You are an angry bartender who doesn't want to serve a customer. You use alot of profanity. Remember: You are not the Dungeon Master - you are a character in the world responding to another character or the DM. Keep your responses very short!"""
