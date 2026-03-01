from tests.fixtures.encounters import encounters_db


def _get_encounter_by_name(name: str):
    for encounter in encounters_db:
        if encounter.name == name:
            return encounter
    raise AssertionError(f"Encounter fixture not found: {name!r}")


def test_encounter_fixtures_all_have_characters():
    missing = [
        encounter.name for encounter in encounters_db if not encounter.character_ids
    ]
    assert missing == [], f"Encounter fixtures missing character_ids: {missing}"


def test_ship_encounter_character_and_player_assignments():
    expected = {
        "The Upper Deck": {"character_ids": [5, 3], "player_ids": [1, 2]},
        "The Main Deck": {"character_ids": [1], "player_ids": [0, 3]},
        "The Captain's Quarters": {"character_ids": [0], "player_ids": [4]},
        "The Hold": {"character_ids": [6], "player_ids": [0]},
        "The Crew Quarters": {"character_ids": [3, 4], "player_ids": [0, 2, 3]},
        "The Lower Deck": {"character_ids": [2], "player_ids": [1, 4]},
    }

    assert {encounter.name for encounter in encounters_db} == set(expected.keys())

    for name, values in expected.items():
        encounter = _get_encounter_by_name(name)
        assert encounter.character_ids == values["character_ids"]
        assert encounter.player_ids == values["player_ids"]
