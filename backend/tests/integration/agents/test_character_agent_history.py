from app.agents.character_agent import CharacterAgent
from app.agents.prompts.import_prompts import import_system_prompt
from tests.fixtures.characters import characters_db
from tests.fixtures.players import players_db
from app.models.nugget import NuggetLayer
from app.services.nugget_service import NuggetService
from app.services.trust_calculator import TrustCalculator
from app.data.trust_store import trust_state_store
from app.data.nugget_store import nugget_store

async def test_character_agent_conversation_history():
    """Test that conversation history is properly maintained across multiple messages with trust nuggets."""
    
    character = characters_db[1]  # Bingo Bracegirdle (tavern keeper)
    player = players_db[2]        # Pippin Greenhill (hobbit rogue)
    
    # Get or create trust state for this character/player combination
    base_trust = TrustCalculator.calculate_base_trust(character, player)
    trust_state = trust_state_store.get_or_create(character.id, player.id, base_trust)
    
    all_nuggets = nugget_store.get_by_character_id(character.id)
    nugget_levels = NuggetService.categorize_nuggets_by_trust(trust_state, all_nuggets)
    
    system_prompt = import_system_prompt("character_agent")
    agent = CharacterAgent(character, player, system_prompt, trust_state)
    
    await agent.chat("What's happening in the village lately?", nugget_levels)
    await agent.chat("Tell me more about any secrets you know", nugget_levels)
    await agent.chat("Do you trust me with sensitive information?", nugget_levels)
    result = await agent.chat("What can you tell me about the town's secrets?", nugget_levels)
    
    messages = result.all_messages()
    # 3x request/response
    assert len(messages) >= 6
