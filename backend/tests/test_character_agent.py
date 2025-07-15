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
    memories = [
        Memory(
            id=1,
            title="Ring Knowledge",
            linked_character_ids=[1],
            visibility_type=VisibilityType.ALWAYS,
            memory_text="The One Ring was forged by the Dark Lord Sauron in the fires of Mount Doom. It contains much of Sauron's power and corrupts those who wear it.",
        ),
        Memory(
            id=2,
            title="World Knowledge",
            linked_character_ids=[1],
            visibility_type=VisibilityType.ALWAYS,
            memory_text="Anyone who wears the one ring becomes a ring wrath.",
        )
    ]
    
    agent = CharacterAgent(character)
    result = await agent.chat("What do you know about the One Ring?", memories)
    
    # Inspect the AgentRunResult
    assert result is not None
    assert hasattr(result, 'output')
    assert isinstance(result.output, str)
    assert len(result.output) > 0
    
    # Verify the agent stored the result
    assert agent.run_result == result
    

    result = await agent.chat("I'm going to put it on. Will you stop me?", memories)

    # Check that we have message history
    messages = result.all_messages()
    assert len(messages) == 4
