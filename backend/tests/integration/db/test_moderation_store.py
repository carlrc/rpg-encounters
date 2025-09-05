#!/usr/bin/env python3
import os

from app.data.moderation_store import ModerationStore
from app.data.user_store import UserStore
from app.db.connection import get_async_db_session
from app.models.moderation import ModerationCreate, ModerationUpdate
from app.models.user import UserCreate


async def test_moderation_store():
    url = os.getenv("TEST_DATABASE_URL")
    async with get_async_db_session(url) as session:
        # Create a user first
        user_data = UserCreate()
        created_user = await UserStore(session=session).create(user_data)

        # Create moderation entries
        moderation_store = ModerationStore(user_id=created_user.id, session=session)

        # First moderation entry
        first_moderation_data = ModerationCreate(
            user_id=created_user.id,
            text="This content has been flagged for inappropriate language.",
            openai_id="mod_abc123",
        )

        created_moderation1 = await moderation_store.create(first_moderation_data)
        assert created_moderation1.id is not None
        assert created_moderation1.user_id == created_user.id
        assert (
            created_moderation1.text
            == "This content has been flagged for inappropriate language."
        )
        assert created_moderation1.openai_id == "mod_abc123"
        assert created_moderation1.created_at is not None

        # Second moderation entry for same user
        second_moderation_data = ModerationCreate(
            user_id=created_user.id,
            text="Content violates community guidelines for spam.",
            openai_id="mod_def456",
        )

        created_moderation2 = await moderation_store.create(second_moderation_data)
        assert created_moderation2.id is not None
        assert created_moderation2.user_id == created_user.id
        assert (
            created_moderation2.text
            == "Content violates community guidelines for spam."
        )
        assert created_moderation2.openai_id == "mod_def456"

        # Test get by id
        retrieved_moderation = await moderation_store.get_by_id(created_moderation1.id)
        assert retrieved_moderation is not None
        assert retrieved_moderation.id == created_moderation1.id
        assert retrieved_moderation.user_id == created_user.id
        assert (
            retrieved_moderation.text
            == "This content has been flagged for inappropriate language."
        )

        # Test get by user id (many-to-one relationship)
        user_moderations = await moderation_store.get_moderations_by_user_id(
            created_user.id
        )
        assert len(user_moderations) == 2
        # Should be ordered by created_at desc
        assert user_moderations[0].id == created_moderation2.id
        assert user_moderations[1].id == created_moderation1.id

        # Test get all moderations
        all_moderations = await moderation_store.get_all()
        assert len(all_moderations) >= 2
        moderation_ids = [mod.id for mod in all_moderations]
        assert created_moderation1.id in moderation_ids
        assert created_moderation2.id in moderation_ids

        # Test update moderation
        update_data = ModerationUpdate(
            text="Updated: Content has been reviewed and flagged for hate speech.",
            openai_id="mod_updated789",
        )
        updated_moderation = await moderation_store.update(
            created_moderation1.id, update_data
        )
        assert updated_moderation is not None
        assert (
            updated_moderation.text
            == "Updated: Content has been reviewed and flagged for hate speech."
        )
        assert updated_moderation.openai_id == "mod_updated789"
        assert updated_moderation.user_id == created_user.id

        # Test moderation exists
        exists = await moderation_store.exists(created_moderation1.id)
        assert exists is True

        # Test delete moderation
        deleted = await moderation_store.delete(created_moderation1.id)
        assert deleted is True

        # Test moderation no longer exists
        exists_after_delete = await moderation_store.exists(created_moderation1.id)
        assert exists_after_delete is False

        # Verify user still has one moderation entry
        remaining_moderations = await moderation_store.get_moderations_by_user_id(
            created_user.id
        )
        assert len(remaining_moderations) == 1
        assert remaining_moderations[0].id == created_moderation2.id

        # Cleanup remaining moderation and user
        await moderation_store.delete(created_moderation2.id)
        await UserStore(user_id=created_user.id, session=session).delete()
