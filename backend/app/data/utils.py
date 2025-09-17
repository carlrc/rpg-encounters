#!/usr/bin/env python3
import argparse
import asyncio
import logging
import sys
from typing import Tuple

from sqlalchemy.exc import SQLAlchemyError

from app.data.account_store import AccountStore
from app.data.user_store import UserStore
from app.data.world_store import WorldStore
from app.db.connection import get_async_db_session
from app.models.account import Account, AccountCreate
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


async def get_account_by_email(email: str) -> Account | None:
    """
    Get account information for a user by email.

    Args:
        email: The email to get account for

    Returns:
        Account object if found, None otherwise

    Raises:
        SQLAlchemyError: If database operations fail
    """
    try:
        account_store = AccountStore(user_id=None)
        account = await account_store.get_by_email(email)

        if account:
            logger.info(f"Found account for email {email}: {account.id}")
            return account
        else:
            logger.info(f"No account found for email {email}")
            return None

    except SQLAlchemyError as e:
        logger.error(f"Error getting account for email {email}: {e}")
        raise


async def main():
    """Main function for CLI usage"""
    parser = argparse.ArgumentParser(
        description="Development utilities for user creation and account retrieval"
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Create user command
    create_parser = subparsers.add_parser(
        "create-user", help="Create a new user with account and world"
    )
    create_parser.add_argument("email", help="Email address for the account")

    # Get account command
    account_parser = subparsers.add_parser(
        "get-account", help="Get account information for a user by email"
    )
    account_parser.add_argument("email", help="Email to get account for")

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

        elif args.command == "get-account":
            account = await get_account_by_email(args.email)
            if account:
                print(f"✅ Found account for email {args.email}:")
                print(f"   User ID: {account.user_id}")
                print(f"   Account ID: {account.id}")
                print(f"   Email: {account.email}")
                print(
                    f"   ElevenLabs Token: {'Set' if account.elevenlabs_token else 'Not set'}"
                )
                print(f"   Created at: {account.created_at}")
            else:
                print(f"❌ No account found for email {args.email}")

    except Exception as e:
        logger.error(f"Command failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
