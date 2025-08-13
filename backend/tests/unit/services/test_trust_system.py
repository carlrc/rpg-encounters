#!/usr/bin/env python3
from app.services.trust_calculator import calculate_base_trust
from tests.fixtures.characters import characters_db
from tests.fixtures.players import players_db


def test_trust_calculation():
    """Test the trust calculation system"""
    character = characters_db[1]  # Bingo Bracegirdle - Halfling Barkeep

    player = players_db[2]  # Pippin Greenhill - Halfling Rogue

    # Calculate base trust using character directly
    base_trust = calculate_base_trust(character, player)

    # Assert that trust calculation works correctly
    # Two matching full bias (e.g., 5+) traits
    assert base_trust == 10
