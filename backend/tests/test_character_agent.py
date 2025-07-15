from app.ai.character_agent import CharacterAgent
from app.models.character import Character, CharacterRace, CharacterSize, CharacterAlignment
from app.models.memory import Memory, VisibilityType
from app.services.memory_manager import MemoryManager

async def test_character_agent_memory_injection():
    """Test that memories are properly injected into the character agent with real API calls."""
    
    # Create test character
    character = Character(
        id=1,
        name="Gandalf",
        race=CharacterRace.HUMAN.value,
        size=CharacterSize.MEDIUM.value,
        alignment=CharacterAlignment.LAWFUL_GOOD.value,
        profession="Wizard",
        background="A wise wizard who has traveled Middle-earth for centuries",
        communication_style="Speaks with wisdom and gravitas",
        tags=["#wizard"]
    )
    
    # Create test memory
    memory = Memory(
        id=1,
        title="Ring Knowledge",
        linked_character_ids=[1],
        visibility_type=VisibilityType.ALWAYS,
        memory_text="The One Ring was forged by the Dark Lord Sauron in the fires of Mount Doom. It contains much of Sauron's power and corrupts those who wear it.",
        character_limit=500
    )
    
    # Create character agent
    agent = CharacterAgent(character)
    
    # Test with real API call
    result = await agent.chat("What do you know about the One Ring?", [memory])
    
    # Inspect the AgentRunResult
    assert result is not None
    assert hasattr(result, 'output')
    assert isinstance(result.output, str)
    assert len(result.output) > 0
    
    # Verify the agent stored the result
    assert agent.run_result == result
    
    # Check that we have message history
    messages = result.all_messages()
    assert len(messages) > 0
    
    print(f"\n=== CHARACTER AGENT TEST RESULTS ===")
    print(f"Character: {character.name}")
    print(f"Memory injected: {memory.title}")
    print(f"Player question: 'What do you know about the One Ring?'")
    print(f"Agent response: {result.output}")
    print(f"Number of messages in history: {len(messages)}")
    print(f"Response length: {len(result.output)} characters")
    
    # Basic assertions about the response
    assert "ring" in result.output.lower() or "sauron" in result.output.lower()
