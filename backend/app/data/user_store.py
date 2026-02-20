import logging
from typing import List

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.data.base_store import BaseStore
from app.db.models.user import UserORM
from app.models.user import User, UserCreate, UserUpdate

logger = logging.getLogger(__name__)


class UserStore(BaseStore):
    def __init__(self, user_id: int | None = None, session: AsyncSession | None = None):
        """Initialize UserStore with user_id to follow the same pattern as other stores"""
        super().__init__(user_id=user_id, world_id=None, session=session)

    async def get_all(self) -> List[User]:
        """Get all users"""
        try:
            async with self.get_session() as session:
                result = await session.execute(select(UserORM))
                user_orms = result.scalars().all()
                return [User.model_validate(user_orm) for user_orm in user_orms]
        except SQLAlchemyError as e:
            logger.error(f"Error getting all users: {e}")
            raise

    async def get_by_id(self, user_id: int) -> User | None:
        """Get a specific user by ID"""
        try:
            async with self.get_session() as session:
                result = await session.execute(
                    select(UserORM).where(UserORM.id == user_id)
                )
                user_orm = result.scalars().first()
                if user_orm:
                    return User.model_validate(user_orm)
                return None
        except SQLAlchemyError as e:
            logger.error(f"Error getting user {user_id}: {e}")
            raise

    async def create(self, user_data: UserCreate) -> User:
        """Create a new user"""
        try:
            async with self.get_session() as session:
                user_orm = UserORM(**user_data.model_dump())
                session.add(user_orm)
                await session.flush()
                await session.refresh(user_orm)
                return User.model_validate(user_orm)
        except SQLAlchemyError as e:
            logger.error(f"Error creating user: {e}")
            raise

    async def update(self, user_id: int, user_update: UserUpdate) -> User | None:
        """Update an existing user"""
        try:
            async with self.get_session() as session:
                result = await session.execute(
                    select(UserORM).where(UserORM.id == user_id)
                )
                user_orm = result.scalars().first()
                if not user_orm:
                    return None

                update_data = user_update.model_dump(exclude_unset=True)
                for key, value in update_data.items():
                    setattr(user_orm, key, value)

                await session.refresh(user_orm)
                return User.model_validate(user_orm)
        except SQLAlchemyError as e:
            logger.error(f"Error updating user {user_id}: {e}")
            raise

    async def delete(self) -> bool:
        """Delete a user"""
        try:
            async with self.get_session() as session:
                result = await session.execute(
                    select(UserORM).where(UserORM.id == self.user_id)
                )
                user_orm = result.scalars().first()
                if not user_orm:
                    return False

                await session.delete(user_orm)
                return True
        except SQLAlchemyError as e:
            logger.error(f"Error deleting user {self.user_id}: {e}")
            raise

    async def exists(self, user_id: int) -> bool:
        """Check if a user exists"""
        try:
            async with self.get_session() as session:
                result = await session.execute(
                    select(UserORM).where(UserORM.id == user_id)
                )
                return result.scalars().first() is not None
        except SQLAlchemyError as e:
            logger.error(f"Error checking if user {user_id} exists: {e}")
            raise
