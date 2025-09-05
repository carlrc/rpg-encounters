import logging
from typing import List, Optional

from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.data.base_store import BaseStore
from app.db.models.account import AccountORM
from app.models.account import Account, AccountCreate, AccountUpdate

logger = logging.getLogger(__name__)


class AccountStore(BaseStore):
    def __init__(self, user_id: Optional[int] = None, session: AsyncSession = None):
        super().__init__(user_id, None, session)

    async def create_account(self, account_data: AccountCreate) -> Account:
        db_account = AccountORM(**account_data.model_dump())
        self.session.add(db_account)
        await self.session.flush()
        await self.session.refresh(db_account)
        return Account.model_validate(db_account)

    async def get_account_by_id(self, account_id: int) -> Optional[Account]:
        result = await self.session.execute(
            select(AccountORM).where(AccountORM.id == account_id)
        )
        account = result.scalar_one_or_none()
        return Account.model_validate(account) if account else None

    async def get_account_by_user_id(self, user_id: int) -> Optional[Account]:
        result = await self.session.execute(
            select(AccountORM).where(AccountORM.user_id == user_id)
        )
        account = result.scalar_one_or_none()
        return Account.model_validate(account) if account else None

    async def get_all_accounts(self) -> List[Account]:
        result = await self.session.execute(select(AccountORM))
        accounts = result.scalars().all()
        return [Account.model_validate(account) for account in accounts]

    async def update_account(
        self, account_id: int, account_update: AccountUpdate
    ) -> Optional[Account]:
        update_data = account_update.model_dump(exclude_unset=True)
        if not update_data:
            return await self.get_account_by_id(account_id)

        await self.session.execute(
            update(AccountORM).where(AccountORM.id == account_id).values(**update_data)
        )
        return await self.get_account_by_id(account_id)

    async def delete_account(self, account_id: int) -> bool:
        result = await self.session.execute(
            delete(AccountORM).where(AccountORM.id == account_id)
        )
        return result.rowcount > 0

    async def account_exists(self, account_id: int) -> bool:
        result = await self.session.execute(
            select(AccountORM.id).where(AccountORM.id == account_id)
        )
        return result.scalar_one_or_none() is not None
