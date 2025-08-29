#!/usr/bin/env python3
import os

from app.data.character_store import CharacterStore
from app.data.influence_store import InfluenceStore
from app.data.player_store import PlayerStore
from app.db.connection import get_db_session
from app.models.character import CharacterCreate
from app.models.influence import Influence
from app.models.player import PlayerCreate
from tests.fixtures.generate import default_character, default_player


def test_influence_store():
    url = os.getenv("TEST_DATABASE_URL")
    with get_db_session(url) as session:
        character_store = CharacterStore(user_id=1, world_id=1, session=session)
        player_store = PlayerStore(user_id=1, world_id=1, session=session)

        # Use generate functions
        character = default_character()
        character_data = CharacterCreate(**character.model_dump(exclude={"id"}))

        player = default_player()
        player_data = PlayerCreate(**player.model_dump(exclude={"id"}))

        created_character = character_store.create_character(character_data)
        created_player = player_store.create_player(player_data)

        # Test influence store
        influence_store = InfluenceStore(user_id=1, world_id=1, session=session)

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
            inf.character_id == created_character.id
            and inf.player_id == created_player.id
            for inf in all_influences
        )

        # Test get_by_character_id
        character_influences = influence_store.get_by_character_id(created_character.id)
        assert len(character_influences) >= 1
        assert all(
            inf.character_id == created_character.id for inf in character_influences
        )

        # Test get_by_player_id
        player_influences = influence_store.get_by_player_id(created_player.id)
        assert len(player_influences) >= 1
        assert all(inf.player_id == created_player.id for inf in player_influences)

        # Test delete_influence
        deleted = influence_store.delete_influence(
            created_character.id, created_player.id
        )
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
