#!/usr/bin/env python3
from app.services.influence_calculator import calculate_base_influence
from tests.fixtures.characters import characters_db
from tests.fixtures.players import players_db


def test_influence_calculation():
    """Test the influence calculation system"""
    character = characters_db[0]  # Bingo Bracegirdle - Halfling Barkeep
    player = players_db[1]  # Pippin Greenhill - Halfing Bard

    # Calculate base influence using character directly
    base_influence = calculate_base_influence(character, player)

    assert base_influence == 10
