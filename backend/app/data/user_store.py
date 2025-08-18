from typing import List

from sqlalchemy.orm import sessionmaker

from app.db.connection import get_db_engine
from app.db.models.user import UserORM
from app.models.user import User, UserCreate, UserUpdate


class UserStore:
    def __init__(self, user_id: int = None):
        """Initialize UserStore with user_id to follow the same pattern as other stores"""
        self.Session = sessionmaker(get_db_engine())
        self.user_id = user_id

    def get_all_users(self) -> List[User]:
        """Get all users"""
        with self.Session() as session:
            user_orms = session.query(UserORM).all()
            return [User.model_validate(user_orm) for user_orm in user_orms]

    def get_user_by_id(self, user_id: int) -> User | None:
        """Get a specific user by ID"""
        with self.Session() as session:
            user_orm = session.query(UserORM).filter(UserORM.id == user_id).first()
            if user_orm:
                return User.model_validate(user_orm)
            return None

    def create_user(self, user_data: UserCreate) -> User:
        """Create a new user"""
        with self.Session() as session:
            user_orm = UserORM(**user_data.model_dump())
            session.add(user_orm)
            session.commit()
            session.refresh(user_orm)
            return User.model_validate(user_orm)

    def update_user(self, user_id: int, user_update: UserUpdate) -> User | None:
        """Update an existing user"""
        with self.Session() as session:
            user_orm = session.query(UserORM).filter(UserORM.id == user_id).first()
            if not user_orm:
                return None

            update_data = user_update.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                setattr(user_orm, key, value)

            session.commit()
            session.refresh(user_orm)
            return User.model_validate(user_orm)

    def delete_user(self) -> bool:
        """Delete a user"""
        with self.Session() as session:
            user_orm = session.query(UserORM).filter(UserORM.id == self.user_id).first()
            if not user_orm:
                return False

            session.delete(user_orm)
            session.commit()
            return True

    def user_exists(self, user_id: int) -> bool:
        """Check if a user exists"""
        with self.Session() as session:
            return (
                session.query(UserORM).filter(UserORM.id == user_id).first() is not None
            )
