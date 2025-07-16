from app.ai.character_agent import CharacterAgent
from app.ai.prompts.import_prompts import import_system_prompt
from tests.fixtures.characters import characters_db
from tests.fixtures.players import players_db
from tests.fixtures.memories import memories_db

async def test_character_agent_memory_injection():
    """Test that memories are properly injected into the character agent with hobbit characters."""
    
    character = characters_db[1]
    player = players_db[2]
    
    memories = [
        memories_db[1],  # The Garden Vandal Mystery
        memories_db[3],  # The Tavern Gossip
    ]
    
    memory_strings = [memory.memory_text for memory in memories]
    
    system_prompt = import_system_prompt()
    agent = CharacterAgent(character, player, system_prompt)
    result = await agent.chat("What's the latest gossip at the tavern about the garden vandalism?", memory_strings)
    
    assert result is not None
    message_history = result.all_messages()

    for memory_text in memory_strings:
        assert memory_text in message_history[0].instructions
    
async def test_character_agent_conversation_history():
    """Test that conversation history is properly maintained across multiple messages."""
    
    # Use same character setup
    character = characters_db[1]  # Bingo Bracegirdle (tavern keeper)
    player = players_db[2]        # Pippin Greenhill (hobbit rogue)
    
    # Use all garden mystery memories for richer context
    memories = [
        memories_db[1],  # The Garden Vandal Mystery
        memories_db[3],  # The Tavern Gossip
        memories_db[4],  # The Competition Connection
    ]
    
    memory_strings = [memory.memory_text for memory in memories]
    
    system_prompt = import_system_prompt()
    agent = CharacterAgent(character, player, system_prompt)
    
    await agent.chat("What's happening in the village lately?", memory_strings)
    await agent.chat("Tell me more about the garden problems", memory_strings)
    await agent.chat("Do you have any suspects?", memory_strings)
    result = await agent.chat("What about the garden competition?", memory_strings)
    
    messages = result.all_messages()
    assert len(messages) == 8
    