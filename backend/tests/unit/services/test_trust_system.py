#!/usr/bin/env python3
import logging
from app.models.nugget import TrustNuggetCreate
from app.data.nugget_store import nugget_store
from app.services.trust_calculator import TrustCalculator
from tests.fixtures.characters import characters_db
from tests.fixtures.players import players_db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def setup_test_data():
    """Set up test characters, players, and nuggets"""

    character = characters_db[1]  # Bingo Bracegirdle - Halfling Barkeep

    player = players_db[2]  # Pippin Greenhill - Halfling Rogue

    nuggets_data = [
        TrustNuggetCreate(
            title="Tavern Knowledge",
            character_ids=[character.id],
            level_1_content="I've been running this tavern for over twenty years and know everyone in town.",
            level_2_content="The mayor has been skimming coins from the town treasury to pay his gambling debts.",
            level_3_content="There's a secret passage behind the wine cellar that leads to the old smuggler's tunnels.",
        )
    ]

    for nugget_data in nuggets_data:
        nugget_store.create_nugget(nugget_data)

    return character, player


def test_trust_calculation():
    """Test the trust calculation system"""
    character, player = setup_test_data()

    # Calculate base trust using character directly
    base_trust = TrustCalculator.calculate_base_trust(character, player)

    # Assert that trust calculation works correctly
    assert base_trust == 0.3
