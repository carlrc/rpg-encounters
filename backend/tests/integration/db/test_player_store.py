#!/usr/bin/env python3
import pytest
from dotenv import load_dotenv

from app.data.player_store import PlayerStore
from app.db.init_db import create_tables, drop_tables
from app.models.alignment import Alignment
from app.models.class_traits import Abilities, Class, Skills
from app.models.player import PlayerCreate, PlayerUpdate
from app.models.race import Gender, Race, Size


@pytest.fixture(autouse=True)
def setup_teardown():
    """Setup and teardown for each test"""
    load_dotenv()
    create_tables()
    yield
    drop_tables()


def test_player_store():
    store = PlayerStore()

    # Test 1: Create a player
    new_player_data = PlayerCreate(
        name="Test Warrior",
        appearance="A brave warrior with shining armor",
        race=Race.HUMAN.value,
        class_name=Class.FIGHTER.value,
        size=Size.MEDIUM.value,
        alignment=Alignment.LAWFUL_GOOD.value,
        gender=Gender.MALE.value,
        abilities={Abilities.CHARISMA.value: 10},
        skills={
            Skills.PERSUASION.value: 5,
            Skills.DECEPTION.value: 2,
            Skills.INTIMIDATION.value: 3,
            Skills.PERFORMANCE.value: 4,
        },
    )

    created_player = store.create_player(new_player_data)
    assert created_player.name == "Test Warrior"
    assert created_player.id is not None

    all_players = store.get_all_players()
    assert len(all_players) >= 1

    retrieved_player = store.get_player_by_id(created_player.id)
    assert retrieved_player is not None
    assert retrieved_player.name == "Test Warrior"

    update_data = PlayerUpdate(
        name="Updated Test Warrior", appearance="A seasoned warrior with battle scars"
    )
    updated_player = store.update_player(created_player.id, update_data)
    assert updated_player is not None
    assert updated_player.name == "Updated Test Warrior"

    exists = store.player_exists(created_player.id)
    assert exists is True

    deleted = store.delete_player(created_player.id)
    assert deleted is True

    exists_after_delete = store.player_exists(created_player.id)
    assert exists_after_delete is False
