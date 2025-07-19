from app.ai.character_agent import CharacterAgent
from app.ai.prompts.import_prompts import import_system_prompt
from tests.fixtures.characters import characters_db
from tests.fixtures.players import players_db
from app.models.nugget import TrustNuggetCreate, NuggetLayer, get_trust_threshold
from app.data.trust_store import trust_state_store
from app.data.nugget_store import nugget_store
from app.services.trust_calculator import TrustCalculator
from app.models.trust import TrustState

async def test_character_agent_nugget_injection():
    """Test that trust nuggets are properly injected into the character agent based on trust levels."""
    
    character = characters_db[1]  # Bingo Bracegirdle - Halfling Barkeep
    player = players_db[2]        # Pippin Greenhill - Halfling Rogue
    
    # Calculate base trust using character directly
    base_trust = TrustCalculator.calculate_base_trust(character, player)
    trust_state = TrustState(
        character_id=character.id,
        player_id=player.id,
        base_trust=base_trust,
        earned_trust=0.0
    )
    trust_state = trust_state_store.update_trust_state(trust_state)
    
    # Create test nuggets for different trust levels
    test_nugget = nugget_store.create_nugget(TrustNuggetCreate(
        title="Tavern Secrets",
        character_ids=[character.id],
        level_1_content="I've been running this tavern for over twenty years and know everyone in town.",
        level_2_content="The mayor has been skimming coins from the town treasury to pay his gambling debts.",
        level_3_content="There's a secret passage behind the wine cellar that leads to the old smuggler's tunnels."
    ))
    
    # Create agent and get accessible nuggets based on trust
    system_prompt = import_system_prompt()
    agent = CharacterAgent(character, player, system_prompt)
    
    # Get trust state to determine accessible nuggets
    trust_state = trust_state_store.get_trust_state(character.id, player.id)
    
    # Get nuggets that should be accessible based on trust level
    accessible_nuggets = []
    all_nuggets = nugget_store.get_by_character_id(character.id)
    
    for nugget in all_nuggets:
        # Add content based on trust level thresholds using enums
        if trust_state.total_trust >= get_trust_threshold(NuggetLayer.PUBLIC):
            accessible_nuggets.append(nugget.level_1_content)
        if trust_state.total_trust >= get_trust_threshold(NuggetLayer.PRIVILEGED):
            accessible_nuggets.append(nugget.level_2_content)
        if trust_state.total_trust >= get_trust_threshold(NuggetLayer.EXCLUSIVE):
            accessible_nuggets.append(nugget.level_3_content)
    
    result = await agent.chat("What's the latest gossip at the tavern?", accessible_nuggets)
    
    assert result is not None
    message_history = result.all_messages()
    
    # Check that accessible nuggets were injected into the agent's instructions
    for nugget_content in accessible_nuggets:
        assert nugget_content in message_history[0].instructions
    
async def test_character_agent_conversation_history():
    """Test that conversation history is properly maintained across multiple messages with trust nuggets."""
    
    character = characters_db[1]  # Bingo Bracegirdle (tavern keeper)
    player = players_db[2]        # Pippin Greenhill (hobbit rogue)
    
    # Get accessible nuggets for this character/player combination
    trust_state = trust_state_store.get_trust_state(character.id, player.id)
    accessible_nuggets = []
    
    if trust_state:
        all_nuggets = nugget_store.get_by_character_id(character.id)
        for nugget in all_nuggets:
            # Add content based on trust level thresholds using enums
            if trust_state.total_trust >= get_trust_threshold(NuggetLayer.PUBLIC):
                accessible_nuggets.append(nugget.level_1_content)
            if trust_state.total_trust >= get_trust_threshold(NuggetLayer.PRIVILEGED):
                accessible_nuggets.append(nugget.level_2_content)
            if trust_state.total_trust >= get_trust_threshold(NuggetLayer.EXCLUSIVE):
                accessible_nuggets.append(nugget.level_3_content)
    
    system_prompt = import_system_prompt()
    agent = CharacterAgent(character, player, system_prompt)
    
    await agent.chat("What's happening in the village lately?", accessible_nuggets)
    await agent.chat("Tell me more about any secrets you know", accessible_nuggets)
    await agent.chat("Do you trust me with sensitive information?", accessible_nuggets)
    result = await agent.chat("What can you tell me about the town's secrets?", accessible_nuggets)
    
    messages = result.all_messages()
    assert len(messages) == 8
