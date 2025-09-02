#!/usr/bin/env python3
import os

from app.data.player_store import PlayerStore
from app.db.connection import get_async_db_session
from app.models.player import PlayerCreate, PlayerUpdate
from tests.fixtures.generate import default_player


async def test_player_store():
    url = os.getenv("TEST_DATABASE_URL")
    async with get_async_db_session(url) as session:
        store = PlayerStore(user_id=1, world_id=1, session=session)

        # Use generate function for player creation
        player = default_player()
        new_player_data = PlayerCreate(**player.model_dump(exclude={"id"}))

        created_player = await store.create_player(new_player_data)
        assert created_player.name == player.name
        assert created_player.id is not None

        all_players = await store.get_all_players()
        assert len(all_players) >= 1

        retrieved_player = await store.get_player_by_id(created_player.id)
        assert retrieved_player is not None
        assert retrieved_player.name == player.name

        update_data = PlayerUpdate(
            name="Updated " + player.name,
            appearance="A seasoned character with experience",
        )
        updated_player = await store.update_player(created_player.id, update_data)
        assert updated_player is not None
        assert updated_player.name == "Updated " + player.name

        exists = await store.player_exists(created_player.id)
        assert exists is True

        deleted = await store.delete_player(created_player.id)
        assert deleted is True

        exists_after_delete = await store.player_exists(created_player.id)
        assert exists_after_delete is False
