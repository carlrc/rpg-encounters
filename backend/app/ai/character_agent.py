from backend.app.models.character import Character
from pydantic_ai import Agent, TextOutput
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider

class CharacterAgent:
    def __init__(self, character: Character):
        self.character = character
        self.agent = Agent(
            OpenAIModel(model_name='mistral', provider=OpenAIProvider(base_url='http://localhost:11434')), 
            output_type=TextOutput,
            deps_type=str,
            system_prompt=character.to_system_prompt())
