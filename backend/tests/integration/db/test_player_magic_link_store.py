#!/usr/bin/env python3

from datetime import datetime, timedelta, timezone

import pytest

from app.data.player_magic_link_store import (
    PlayerMagicLinkStore,
    PlayerTokenAlreadyUsedError,
    PlayerTokenExpiredError,
    PlayerTokenNotFoundError,
)
from app.data.player_store import PlayerStore
from app.data.user_store import UserStore
from app.data.world_store import WorldStore
from app.db.connection import get_async_db_session
from app.db.models.player_magic_link import PlayerMagicLinkORM
from app.models.player import PlayerCreate
from app.models.player_magic_link import PlayerMagicLinkCreate
from app.models.user import UserCreate
from app.utils import get_or_throw
from tests.fixtures.generate import create_opposing_barbarian_player, default_player


async def test_player_magic_link_create_and_retrieve():
    """Test creating a player magic link and verifying its properties"""
    url = get_or_throw("TEST_DATABASE_URL")
    async with get_async_db_session(url) as session:
        # Create user (DM) and world
        user_store = UserStore(session=session)
        user = await user_store.create(UserCreate())

        world_store = WorldStore(user_id=user.id, session=session)
        world = await world_store.create()

        # Create player using generate.py fixture
        player_store = PlayerStore(user_id=user.id, world_id=world.id, session=session)
        player_data = default_player(player_id=1)
        player_create = PlayerCreate(**player_data.model_dump(exclude={"id"}))
        player = await player_store.create(player_create)

        # Create player magic link
        player_magic_link_store = PlayerMagicLinkStore(session=session)
        raw_token = PlayerMagicLinkStore.generate_token()
        token_hash = PlayerMagicLinkStore.hash_token(raw_token)

        magic_link_data = PlayerMagicLinkCreate(
            player_id=player.id,
            user_id=user.id,
            world_id=world.id,
            token_hash=token_hash,
            expires_at=PlayerMagicLinkStore.magic_link_expiry(),
            used=False,
        )

        magic_link = await player_magic_link_store.create(magic_link_data)

        # Verify link properties
        assert magic_link.player_id == player.id
        assert magic_link.user_id == user.id
        assert magic_link.world_id == world.id
        assert magic_link.used is False
        assert magic_link.expires_at > datetime.now(timezone.utc)
        assert magic_link.id is not None
        assert magic_link.created_at is not None
        assert raw_token is not None
        assert len(raw_token) > 0


async def test_player_magic_link_consume_success():
    """Test successfully consuming a player magic link"""
    url = get_or_throw("TEST_DATABASE_URL")
    async with get_async_db_session(url) as session:
        # Create user, world, and player
        user_store = UserStore(session=session)
        user = await user_store.create(UserCreate())

        world_store = WorldStore(user_id=user.id, session=session)
        world = await world_store.create()

        player_store = PlayerStore(user_id=user.id, world_id=world.id, session=session)
        player_data = default_player(player_id=1)
        player_create = PlayerCreate(**player_data.model_dump(exclude={"id"}))
        player = await player_store.create(player_create)

        # Create player magic link
        player_magic_link_store = PlayerMagicLinkStore(session=session)
        raw_token = PlayerMagicLinkStore.generate_token()
        token_hash = PlayerMagicLinkStore.hash_token(raw_token)

        magic_link_data = PlayerMagicLinkCreate(
            player_id=player.id,
            user_id=user.id,
            world_id=world.id,
            token_hash=token_hash,
            expires_at=PlayerMagicLinkStore.magic_link_expiry(),
            used=False,
        )

        created_link = await player_magic_link_store.create(magic_link_data)

        # Consume the magic link
        token_hash = PlayerMagicLinkStore.hash_token(raw_token)
        consumed_link = await player_magic_link_store.consume(token_hash)

        # Verify consumption
        assert consumed_link.id == created_link.id
        assert consumed_link.player_id == player.id
        assert consumed_link.user_id == user.id
        assert consumed_link.world_id == world.id
        assert consumed_link.used is True
        assert consumed_link.used_at is not None
        assert consumed_link.used_at > created_link.created_at


async def test_player_magic_link_consume_expired():
    """Test consuming an expired player magic link"""
    url = get_or_throw("TEST_DATABASE_URL")
    async with get_async_db_session(url) as session:
        # Create user, world, and player
        user_store = UserStore(session=session)
        user = await user_store.create(UserCreate())

        world_store = WorldStore(user_id=user.id, session=session)
        world = await world_store.create()

        player_store = PlayerStore(user_id=user.id, world_id=world.id, session=session)
        player_data = default_player(player_id=1)
        player_create = PlayerCreate(**player_data.model_dump(exclude={"id"}))
        player = await player_store.create(player_create)

        # Create expired player magic link
        player_magic_link_store = PlayerMagicLinkStore(session=session)
        raw_token = PlayerMagicLinkStore.generate_token()
        expired_time = datetime.now(timezone.utc) - timedelta(hours=1)

        magic_link_data = PlayerMagicLinkCreate(
            player_id=player.id,
            user_id=user.id,
            world_id=world.id,
            token_hash=PlayerMagicLinkStore.hash_token(raw_token),
            expires_at=expired_time,
            used=False,
        )

        # Manually create expired link
        magic_link_orm = PlayerMagicLinkORM(**magic_link_data.model_dump())
        session.add(magic_link_orm)
        await session.flush()

        # Try to consume expired link
        token_hash = PlayerMagicLinkStore.hash_token(raw_token)
        with pytest.raises(PlayerTokenExpiredError):
            await player_magic_link_store.consume(token_hash)


async def test_player_magic_link_consume_already_used():
    """Test consuming an already used player magic link"""
    url = get_or_throw("TEST_DATABASE_URL")
    async with get_async_db_session(url) as session:
        # Create user, world, and player
        user_store = UserStore(session=session)
        user = await user_store.create(UserCreate())

        world_store = WorldStore(user_id=user.id, session=session)
        world = await world_store.create()

        player_store = PlayerStore(user_id=user.id, world_id=world.id, session=session)
        player_data = default_player(player_id=1)
        player_create = PlayerCreate(**player_data.model_dump(exclude={"id"}))
        player = await player_store.create(player_create)

        # Create player magic link
        player_magic_link_store = PlayerMagicLinkStore(session=session)
        raw_token = PlayerMagicLinkStore.generate_token()
        token_hash = PlayerMagicLinkStore.hash_token(raw_token)

        magic_link_data = PlayerMagicLinkCreate(
            player_id=player.id,
            user_id=user.id,
            world_id=world.id,
            token_hash=token_hash,
            expires_at=PlayerMagicLinkStore.magic_link_expiry(),
            used=False,
        )

        await player_magic_link_store.create(magic_link_data)

        # Consume the link once
        token_hash = PlayerMagicLinkStore.hash_token(raw_token)
        await player_magic_link_store.consume(token_hash)

        # Try to consume again
        with pytest.raises(PlayerTokenAlreadyUsedError):
            await player_magic_link_store.consume(token_hash)


async def test_player_magic_link_consume_not_found():
    """Test consuming with non-existent token"""
    url = get_or_throw("TEST_DATABASE_URL")
    async with get_async_db_session(url) as session:
        player_magic_link_store = PlayerMagicLinkStore(session=session)

        # Try to consume non-existent token
        fake_token = PlayerMagicLinkStore.generate_token()
        token_hash = PlayerMagicLinkStore.hash_token(fake_token)

        with pytest.raises(PlayerTokenNotFoundError):
            await player_magic_link_store.consume(token_hash)


async def test_multiple_player_links_same_player():
    """Test creating multiple magic links for the same player"""
    url = get_or_throw("TEST_DATABASE_URL")
    async with get_async_db_session(url) as session:
        # Create user, world, and player
        user_store = UserStore(session=session)
        user = await user_store.create(UserCreate())

        world_store = WorldStore(user_id=user.id, session=session)
        world = await world_store.create()

        player_store = PlayerStore(user_id=user.id, world_id=world.id, session=session)
        player_data = default_player(player_id=1)
        player_create = PlayerCreate(**player_data.model_dump(exclude={"id"}))
        player = await player_store.create(player_create)

        # Create multiple magic links
        player_magic_link_store = PlayerMagicLinkStore(session=session)
        links = []

        for _ in range(3):
            raw_token = PlayerMagicLinkStore.generate_token()
            token_hash = PlayerMagicLinkStore.hash_token(raw_token)

            magic_link_data = PlayerMagicLinkCreate(
                player_id=player.id,
                user_id=user.id,
                world_id=world.id,
                token_hash=token_hash,
                expires_at=PlayerMagicLinkStore.magic_link_expiry(),
                used=False,
            )

            magic_link = await player_magic_link_store.create(magic_link_data)
            links.append((magic_link, raw_token))

        # Verify all links exist and are independent
        assert len(links) == 3
        for magic_link, raw_token in links:
            assert magic_link.player_id == player.id
            assert magic_link.user_id == user.id
            assert magic_link.world_id == world.id
            assert magic_link.used is False

        # Consume one link
        first_link, first_token = links[0]
        token_hash = PlayerMagicLinkStore.hash_token(first_token)
        consumed = await player_magic_link_store.consume(token_hash)

        assert consumed.id == first_link.id
        assert consumed.used is True

        # Verify other links are still unused
        second_link, second_token = links[1]
        token_hash2 = PlayerMagicLinkStore.hash_token(second_token)
        still_valid = await player_magic_link_store.consume(token_hash2)

        assert still_valid.id == second_link.id
        assert still_valid.used is True


async def test_player_link_no_device_binding():
    """Test that player magic links don't require device binding"""
    url = get_or_throw("TEST_DATABASE_URL")
    async with get_async_db_session(url) as session:
        # Create user, world, and player
        user_store = UserStore(session=session)
        user = await user_store.create(UserCreate())

        world_store = WorldStore(user_id=user.id, session=session)
        world = await world_store.create()

        player_store = PlayerStore(user_id=user.id, world_id=world.id, session=session)
        player_data = default_player(player_id=1)
        player_create = PlayerCreate(**player_data.model_dump(exclude={"id"}))
        player = await player_store.create(player_create)

        # Create player magic link
        player_magic_link_store = PlayerMagicLinkStore(session=session)
        raw_token = PlayerMagicLinkStore.generate_token()
        token_hash = PlayerMagicLinkStore.hash_token(raw_token)

        magic_link_data = PlayerMagicLinkCreate(
            player_id=player.id,
            user_id=user.id,
            world_id=world.id,
            token_hash=token_hash,
            expires_at=PlayerMagicLinkStore.magic_link_expiry(),
            used=False,
        )

        magic_link = await player_magic_link_store.create(magic_link_data)

        # Consume without device binding - should work
        token_hash = PlayerMagicLinkStore.hash_token(raw_token)
        consumed_link = await player_magic_link_store.consume(token_hash)

        assert consumed_link.id == magic_link.id
        assert consumed_link.used is True


async def test_different_players_for_comparison():
    """Test magic links for different player types"""
    url = get_or_throw("TEST_DATABASE_URL")
    async with get_async_db_session(url) as session:
        # Create user and world
        user_store = UserStore(session=session)
        user = await user_store.create(UserCreate())

        world_store = WorldStore(user_id=user.id, session=session)
        world = await world_store.create()

        player_store = PlayerStore(user_id=user.id, world_id=world.id, session=session)

        # Create bard player using default_player
        bard_data = default_player(player_id=1)
        bard_create = PlayerCreate(**bard_data.model_dump(exclude={"id"}))
        bard_player = await player_store.create(bard_create)

        # Create barbarian player using opposing player fixture
        barbarian_data = create_opposing_barbarian_player(player_id=2)
        barbarian_create = PlayerCreate(**barbarian_data.model_dump(exclude={"id"}))
        barbarian_player = await player_store.create(barbarian_create)

        # Create magic links for both players
        player_magic_link_store = PlayerMagicLinkStore(session=session)

        bard_token = PlayerMagicLinkStore.generate_token()
        bard_token_hash = PlayerMagicLinkStore.hash_token(bard_token)

        bard_magic_link_data = PlayerMagicLinkCreate(
            player_id=bard_player.id,
            user_id=user.id,
            world_id=world.id,
            token_hash=bard_token_hash,
            expires_at=PlayerMagicLinkStore.magic_link_expiry(),
            used=False,
        )

        bard_link = await player_magic_link_store.create(bard_magic_link_data)

        barbarian_token = PlayerMagicLinkStore.generate_token()
        barbarian_token_hash = PlayerMagicLinkStore.hash_token(barbarian_token)

        barbarian_magic_link_data = PlayerMagicLinkCreate(
            player_id=barbarian_player.id,
            user_id=user.id,
            world_id=world.id,
            token_hash=barbarian_token_hash,
            expires_at=PlayerMagicLinkStore.magic_link_expiry(),
            used=False,
        )

        barbarian_link = await player_magic_link_store.create(barbarian_magic_link_data)

        # Verify links are independent
        assert bard_link.player_id == bard_player.id
        assert barbarian_link.player_id == barbarian_player.id
        assert bard_link.id != barbarian_link.id
        assert bard_token != barbarian_token

        # Verify both can be consumed independently
        bard_hash = PlayerMagicLinkStore.hash_token(bard_token)
        consumed_bard = await player_magic_link_store.consume(bard_hash)
        assert consumed_bard.player_id == bard_player.id
        assert consumed_bard.used is True

        barbarian_hash = PlayerMagicLinkStore.hash_token(barbarian_token)
        consumed_barbarian = await player_magic_link_store.consume(barbarian_hash)
        assert consumed_barbarian.player_id == barbarian_player.id
        assert consumed_barbarian.used is True
