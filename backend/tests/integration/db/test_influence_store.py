#!/usr/bin/env python3
import pytest
from dotenv import load_dotenv

from app.data.character_store import CharacterStore
from app.data.influence_store import InfluenceStore
from app.data.player_store import PlayerStore
from app.db.init_db import create_tables, drop_tables
from app.models.alignment import Alignment
from app.models.character import CharacterCreate
from app.models.class_traits import Abilities, Class, Skills
from app.models.influence import Influence
from app.models.player import PlayerCreate
from app.models.race import Gender, Race, Size


@pytest.fixture(autouse=True)
def setup_teardown():
    """Setup and teardown for each test"""
    load_dotenv()
    create_tables()
    yield
    drop_tables()


def test_influence_store():
    # Create character and player first
    character_store = CharacterStore()
    player_store = PlayerStore()

    character_data = CharacterCreate(
        name="Test Wizard",
        avatar=None,
        race=Race.HIGH_ELF.value,
        size=Size.MEDIUM.value,
        alignment=Alignment.CHAOTIC_GOOD.value,
        gender=Gender.FEMALE.value,
        profession="Court Wizard",
        background="A wise elf who studied magic in the ancient libraries.",
        communication_style="Speaks with measured words and ancient wisdom.",
        motivation="Seeks to preserve ancient magical knowledge.",
        personality="",
        voice="JBFqnCBsd6RMkjVDRZzb",
        race_preferences={Race.HIGH_ELF.value: 2},
        class_preferences={Class.WIZARD.value: 3},
        gender_preferences={Gender.FEMALE.value: 1},
        size_preferences={Size.MEDIUM.value: 1},
    )

    player_data = PlayerCreate(
        name="Test Player",
        appearance="A tall elf with flowing silver hair",
        race=Race.HIGH_ELF.value,
        class_name=Class.WIZARD.value,
        size=Size.MEDIUM.value,
        alignment=Alignment.CHAOTIC_GOOD.value,
        gender=Gender.FEMALE.value,
        abilities={Abilities.CHARISMA.value: 10},
        skills={
            Skills.PERSUASION.value: 5,
            Skills.DECEPTION.value: 2,
            Skills.INTIMIDATION.value: 3,
            Skills.PERFORMANCE.value: 4,
        },
    )

    created_character = character_store.create_character(character_data)
    created_player = player_store.create_player(player_data)

    # Test influence store
    influence_store = InfluenceStore()

    # Test get_or_create - new influence
    base_influence = 5
    influence = influence_store.get_or_create(
        created_character.id, created_player.id, base_influence
    )
    assert influence.character_id == created_character.id
    assert influence.player_id == created_player.id
    assert influence.base == base_influence
    assert influence.earned == 0
    assert influence.score == base_influence

    # Test get_or_create - existing influence
    existing_influence = influence_store.get_or_create(
        created_character.id, created_player.id, 10
    )
    assert existing_influence.base == base_influence  # Should not change
    assert existing_influence.earned == 0

    # Test get_influence
    retrieved_influence = influence_store.get_influence(
        created_character.id, created_player.id
    )
    assert retrieved_influence is not None
    assert retrieved_influence.base == base_influence

    # Test update_influence
    updated_influence = Influence(
        character_id=created_character.id,
        player_id=created_player.id,
        base=base_influence,
        earned=3,
    )
    result = influence_store.update_influence(updated_influence)
    assert result.earned == 3
    assert result.score == base_influence + 3

    # Test reset_influence
    reset_success = influence_store.reset_influence(
        created_character.id, created_player.id
    )
    assert reset_success is True

    reset_influence = influence_store.get_influence(
        created_character.id, created_player.id
    )
    assert reset_influence.earned == 0
    assert reset_influence.base == base_influence  # Base should remain

    # Test get_all_influences
    all_influences = influence_store.get_all_influences()
    assert len(all_influences) >= 1
    assert any(
        inf.character_id == created_character.id and inf.player_id == created_player.id
        for inf in all_influences
    )

    # Test get_by_character_id
    character_influences = influence_store.get_by_character_id(created_character.id)
    assert len(character_influences) >= 1
    assert all(inf.character_id == created_character.id for inf in character_influences)

    # Test get_by_player_id
    player_influences = influence_store.get_by_player_id(created_player.id)
    assert len(player_influences) >= 1
    assert all(inf.player_id == created_player.id for inf in player_influences)

    # Test delete_influence
    deleted = influence_store.delete_influence(created_character.id, created_player.id)
    assert deleted is True

    # Verify deletion
    deleted_influence = influence_store.get_influence(
        created_character.id, created_player.id
    )
    assert deleted_influence is None

    # Test delete non-existent influence
    deleted_again = influence_store.delete_influence(
        created_character.id, created_player.id
    )
    assert deleted_again is False

    # Test clear
    influence_store.get_or_create(created_character.id, created_player.id, 5)
    influence_store.clear()
    all_after_clear = influence_store.get_all_influences()
    assert len(all_after_clear) == 0
