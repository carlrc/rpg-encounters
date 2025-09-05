import logging
from typing import List

from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.data.base_store import BaseStore
from app.db.models.account import AccountORM
from app.models.account import Account, AccountCreate, AccountUpdate

logger = logging.getLogger(__name__)


class AccountStore(BaseStore):
    def __init__(self, user_id: int, session: AsyncSession = None):
        super().__init__(user_id=user_id, world_id=None, session=session)

    async def create(self, account_data: AccountCreate) -> Account:
        async with self.get_session() as session:
            db_account = AccountORM(**account_data.model_dump())
            session.add(db_account)
            await session.flush()
            await session.refresh(db_account)
            return Account.model_validate(db_account)

    async def get_by_id(self, account_id: int) -> Account | None:
        async with self.get_session() as session:
            result = await session.execute(
                select(AccountORM).where(AccountORM.id == account_id)
            )
            account = result.scalar_one_or_none()
            return Account.model_validate(account) if account else None

    async def get_account_by_user_id(self, user_id: int) -> Account | None:
        async with self.get_session() as session:
            result = await session.execute(
                select(AccountORM).where(AccountORM.user_id == user_id)
            )
            account = result.scalar_one_or_none()
            return Account.model_validate(account) if account else None

    async def get_all(self) -> List[Account]:
        async with self.get_session() as session:
            result = await session.execute(select(AccountORM))
            accounts = result.scalars().all()
            return [Account.model_validate(account) for account in accounts]

    async def update(
        self, account_id: int, account_update: AccountUpdate
    ) -> Account | None:
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

    async def delete(self, account_id: int) -> bool:
        async with self.get_session() as session:
            result = await session.execute(
                delete(AccountORM).where(AccountORM.id == account_id)
            )
            return result.rowcount > 0

    async def exists(self, account_id: int) -> bool:
        async with self.get_session() as session:
            result = await session.execute(
                select(AccountORM.id).where(AccountORM.id == account_id)
            )
            return result.scalar_one_or_none() is not None
