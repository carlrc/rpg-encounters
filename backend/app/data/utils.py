#!/usr/bin/env python3
import argparse
import asyncio
import logging
import sys
from typing import Tuple

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from app.data.account_store import AccountStore
from app.data.magic_link_store import MagicLinkStore
from app.data.user_store import UserStore
from app.data.world_store import WorldStore
from app.db.connection import get_async_db_session
from app.db.models.magic_link import MagicLinkORM
from app.models.account import Account, AccountCreate
from app.models.magic_link import MagicLink
from app.models.user import User, UserCreate
from app.models.world import World

logger = logging.getLogger(__name__)


async def create_new_user(email: str) -> Tuple[User, Account, World]:
    """
    Create a new user with account and world for testing purposes.

    Args:
        email: Email address for the account

    Returns:
        Tuple of (User, Account, World) objects

    Raises:
        SQLAlchemyError: If database operations fail
    """
    try:
        async with get_async_db_session() as session:
            # Use shared session across all stores
            user_store = UserStore(session=session)
            user = await user_store.create(UserCreate())
            logger.info(f"Created user with ID: {user.id}")

            # Create account
            account_store = AccountStore(user_id=user.id, session=session)
            account = await account_store.create(
                AccountCreate(user_id=user.id, email=email)
            )
            logger.info(f"Created account with email: {email}")

            # Create world
            world_store = WorldStore(user_id=user.id, session=session)
            world = await world_store.create()
            logger.info(f"Created world with ID: {world.id}")

            return user, account, world

    except SQLAlchemyError as e:
        logger.error(f"Error creating user with email {email}: {e}")
        raise


async def get_latest_magic_link_for_user(user_id: int) -> MagicLink | None:
    """
    Get the most recent magic link for a user.

    Args:
        user_id: The user ID to get magic link for

    Returns:
        MagicLink object if found, None otherwise

    Raises:
        SQLAlchemyError: If database operations fail
    """
    try:
        magic_link_store = MagicLinkStore()
        async with magic_link_store.get_session() as session:
            result = await session.execute(
                select(MagicLinkORM)
                .where(MagicLinkORM.user_id == user_id)
                .order_by(MagicLinkORM.created_at.desc())
                .limit(1)
            )
            magic_link_orm = result.scalar_one_or_none()

            if magic_link_orm:
                magic_link = MagicLink.model_validate(magic_link_orm)
                logger.info(f"Found magic link for user {user_id}: {magic_link.id}")
                return magic_link
            else:
                logger.info(f"No magic link found for user {user_id}")
                return None

    except SQLAlchemyError as e:
        logger.error(f"Error getting magic link for user {user_id}: {e}")
        raise


async def main():
    """Main function for CLI usage"""
    parser = argparse.ArgumentParser(
        description="Development utilities for user creation and magic link retrieval"
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Create user command
    create_parser = subparsers.add_parser(
        "create-user", help="Create a new user with account and world"
    )
    create_parser.add_argument("email", help="Email address for the account")

    # Get magic link command
    magic_parser = subparsers.add_parser(
        "get-magic-link", help="Get the latest magic link for a user"
    )
    magic_parser.add_argument("user_id", type=int, help="User ID to get magic link for")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    try:
        if args.command == "create-user":
            user, account, world = await create_new_user(args.email)
            print("✅ Created user successfully!")
            print(f"   User ID: {user.id}")
            print(f"   Email: {account.email}")
            print(f"   World ID: {world.id}")
            print(f"   Created at: {user.created_at}")

        elif args.command == "get-magic-link":
            magic_link = await get_latest_magic_link_for_user(args.user_id)
            if magic_link:
                print(f"✅ Found magic link for user {args.user_id}:")
                print(f"   Created at: {magic_link.created_at}")
                print(f"   Expires at: {magic_link.expires_at}")
                print(f"   Used: {magic_link.used}")
                if magic_link.used_at:
                    print(f"   Used at: {magic_link.used_at}")
            else:
                print(f"❌ No magic link found for user {args.user_id}")

    except Exception as e:
        logger.error(f"Command failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
