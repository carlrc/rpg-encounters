import logging
from typing import List

from async_lru import alru_cache
from sqlalchemy import delete, select, update
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.data.base_store import BaseStore
from app.db.models.account import AccountORM
from app.models.account import Account, AccountCreate, AccountUpdate

logger = logging.getLogger(__name__)


@alru_cache()
async def get_user_elevenlabs_token(user_id: int) -> str | None:
    """Check if user has ElevenLabs token configured - with LRU cache"""
    try:
        account = await AccountStore(user_id=user_id).get_account_by_user_id(user_id)
        return account.elevenlabs_token if account else None
    except Exception as e:
        logger.error(f"Failed to check ElevenLabs token for user {user_id}: {e}")
        return None


class AccountStore(BaseStore):
    def __init__(self, user_id: int | None, session: AsyncSession = None):
        super().__init__(user_id=user_id, world_id=None, session=session)

    async def create(self, account_data: AccountCreate) -> Account:
        try:
            async with self.get_session() as session:
                db_account = AccountORM(**account_data.model_dump())
                session.add(db_account)
                await session.flush()
                await session.refresh(db_account)
                return Account.model_validate(db_account)
        except SQLAlchemyError as e:
            logger.error(f"Error creating account for user {self.user_id}: {e}")
            raise

    async def get_by_id(self, account_id: int) -> Account | None:
        try:
            async with self.get_session() as session:
                result = await session.execute(
                    select(AccountORM).where(AccountORM.id == account_id)
                )
                account = result.scalar_one_or_none()
                return Account.model_validate(account) if account else None
        except SQLAlchemyError as e:
            logger.error(
                f"Error getting account {account_id} for user {self.user_id}: {e}"
            )
            raise

    async def get_account_by_user_id(self, user_id: int) -> Account | None:
        try:
            async with self.get_session() as session:
                result = await session.execute(
                    select(AccountORM).where(AccountORM.user_id == user_id)
                )
                account = result.scalar_one_or_none()
                return Account.model_validate(account) if account else None
        except SQLAlchemyError as e:
            logger.error(f"Error getting account by user {user_id}: {e}")
            raise

    async def get_by_email(self, email: str) -> Account | None:
        try:
            async with self.get_session() as session:
                result = await session.execute(
                    select(AccountORM).where(AccountORM.email == email)
                )
                account = result.scalar_one_or_none()
                return Account.model_validate(account) if account else None
        except SQLAlchemyError as e:
            logger.error(f"Error getting account by email {email}: {e}")
            raise

    async def get_all(self) -> List[Account]:
        try:
            async with self.get_session() as session:
                result = await session.execute(select(AccountORM))
                accounts = result.scalars().all()
                return [Account.model_validate(account) for account in accounts]
        except SQLAlchemyError as e:
            logger.error(f"Error getting all accounts for user {self.user_id}: {e}")
            raise

    async def update(
        self, account_id: int, account_update: AccountUpdate
    ) -> Account | None:
        try:
            update_data = account_update.model_dump(exclude_unset=True)
            if not update_data:
                return await self.get_by_id(account_id)

            async with self.get_session() as session:
                await session.execute(
                    update(AccountORM)
                    .where(AccountORM.id == account_id)
                    .values(**update_data)
                )
            return await self.get_by_id(account_id)
        except SQLAlchemyError as e:
            logger.error(
                f"Error updating account {account_id} for user {self.user_id}: {e}"
            )
            raise

    async def delete(self, account_id: int) -> bool:
        try:
            async with self.get_session() as session:
                result = await session.execute(
                    delete(AccountORM).where(AccountORM.id == account_id)
                )
                return result.rowcount > 0
        except SQLAlchemyError as e:
            logger.error(
                f"Error deleting account {account_id} for user {self.user_id}: {e}"
            )
            raise

    async def exists(self, account_id: int) -> bool:
        try:
            async with self.get_session() as session:
                result = await session.execute(
                    select(AccountORM.id).where(AccountORM.id == account_id)
                )
                return result.scalar_one_or_none() is not None
        except SQLAlchemyError as e:
            logger.error(
                f"Error checking if account {account_id} exists for user {self.user_id}: {e}"
            )
            raise
