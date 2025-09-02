from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.data.base_store import BaseStore
from app.db.models.user import UserORM
from app.models.user import User, UserCreate, UserUpdate


class UserStore(BaseStore):
    def __init__(self, user_id: int = None, session: AsyncSession = None):
        """Initialize UserStore with user_id to follow the same pattern as other stores"""
        super().__init__(user_id=user_id, world_id=None, session=session)

    async def get_all_users(self) -> List[User]:
        """Get all users"""
        async with self.get_session() as session:
            result = await session.execute(select(UserORM))
            user_orms = result.scalars().all()
            return [User.model_validate(user_orm) for user_orm in user_orms]

    async def get_user_by_id(self, user_id: int) -> User | None:
        """Get a specific user by ID"""
        async with self.get_session() as session:
            result = await session.execute(select(UserORM).where(UserORM.id == user_id))
            user_orm = result.scalars().first()
            if user_orm:
                return User.model_validate(user_orm)
            return None

    async def create_user(self, user_data: UserCreate) -> User:
        """Create a new user"""
        async with self.get_session() as session:
            user_orm = UserORM(**user_data.model_dump())
            session.add(user_orm)
            await session.flush()
            await session.refresh(user_orm)
            return User.model_validate(user_orm)

    async def update_user(self, user_id: int, user_update: UserUpdate) -> User | None:
        """Update an existing user"""
        async with self.get_session() as session:
            result = await session.execute(select(UserORM).where(UserORM.id == user_id))
            user_orm = result.scalars().first()
            if not user_orm:
                return None

            update_data = user_update.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                setattr(user_orm, key, value)

            await session.refresh(user_orm)
            return User.model_validate(user_orm)

    async def delete_user(self) -> bool:
        """Delete a user"""
        async with self.get_session() as session:
            result = await session.execute(
                select(UserORM).where(UserORM.id == self.user_id)
            )
            user_orm = result.scalars().first()
            if not user_orm:
                return False

            await session.delete(user_orm)
            return True

    async def user_exists(self, user_id: int) -> bool:
        """Check if a user exists"""
        async with self.get_session() as session:
            result = await session.execute(select(UserORM).where(UserORM.id == user_id))
            return result.scalars().first() is not None
