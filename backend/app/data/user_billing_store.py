import logging

from sqlalchemy import delete, select, update
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.data.base_store import BaseStore
from app.db.models.user_billing import UserBillingORM
from app.models.user_billing import UserBilling, UserBillingCreate, UserBillingUpdate

logger = logging.getLogger(__name__)


class UserBillingStore(BaseStore):
    def __init__(self, user_id: int, session: AsyncSession | None = None):
        super().__init__(user_id=user_id, world_id=None, session=session)

    async def create(self, user_billing_data: UserBillingCreate) -> UserBilling:
        try:
            async with self.get_session() as session:
                db_user_billing = UserBillingORM(**user_billing_data.model_dump())
                session.add(db_user_billing)
                await session.flush()
                await session.refresh(db_user_billing)
                return UserBilling.model_validate(db_user_billing)
        except SQLAlchemyError as e:
            logger.error(f"Error creating user billing for user {self.user_id}: {e}")
            raise

    async def get_by_user_id(self, user_id: int) -> UserBilling | None:
        try:
            async with self.get_session() as session:
                result = await session.execute(
                    select(UserBillingORM).where(UserBillingORM.user_id == user_id)
                )
                user_billing = result.scalar_one_or_none()
                return (
                    UserBilling.model_validate(user_billing) if user_billing else None
                )
        except SQLAlchemyError as e:
            logger.error(f"Error getting user billing by user {user_id}: {e}")
            raise

    async def get_or_create(self, user_id: int) -> UserBilling:
        try:
            existing = await self.get_by_user_id(user_id)
            if existing:
                return existing

            return await self.create(
                UserBillingCreate(
                    user_id=user_id,
                    available_tokens=0,
                    last_used_tokens=0,
                    total_used_tokens=0,
                )
            )
        except SQLAlchemyError as e:
            logger.error(f"Error get_or_create user billing by user {user_id}: {e}")
            raise

    async def update_by_user_id(
        self, user_id: int, user_billing_update: UserBillingUpdate
    ) -> UserBilling | None:
        try:
            update_data = user_billing_update.model_dump(exclude_unset=True)
            if not update_data:
                return await self.get_by_user_id(user_id)

            async with self.get_session() as session:
                await session.execute(
                    update(UserBillingORM)
                    .where(UserBillingORM.user_id == user_id)
                    .values(**update_data)
                )
            return await self.get_by_user_id(user_id)
        except SQLAlchemyError as e:
            logger.error(f"Error updating user billing by user {user_id}: {e}")
            raise

    async def delete_by_user_id(self, user_id: int) -> bool:
        try:
            async with self.get_session() as session:
                result = await session.execute(
                    delete(UserBillingORM).where(UserBillingORM.user_id == user_id)
                )
                return result.rowcount > 0
        except SQLAlchemyError as e:
            logger.error(f"Error deleting user billing by user {user_id}: {e}")
            raise

    async def get_orm_for_update(self, user_id: int) -> UserBillingORM:
        if not self.session:
            raise RuntimeError("get_orm_for_update requires a shared DB session")

        try:
            async with self.get_session() as session:
                result = await session.execute(
                    select(UserBillingORM)
                    .where(UserBillingORM.user_id == user_id)
                    .with_for_update()
                )
                user_billing = result.scalar_one_or_none()
                if user_billing:
                    return user_billing

                user_billing = UserBillingORM(
                    user_id=user_id,
                    available_tokens=0,
                    last_used_tokens=0,
                    total_used_tokens=0,
                )
                session.add(user_billing)
                await session.flush()
                await session.refresh(user_billing)
                return user_billing
        except SQLAlchemyError as e:
            logger.error(f"Error locking user billing by user {user_id}: {e}")
            raise

    async def apply_usage_delta(self, user_id: int, usage_delta: int) -> UserBilling:
        billing = await self.get_orm_for_update(user_id=user_id)
        new_total_used_tokens = billing.total_used_tokens + usage_delta
        new_available_tokens = billing.available_tokens - usage_delta
        updated = await self.update_by_user_id(
            user_id=user_id,
            user_billing_update=UserBillingUpdate(
                available_tokens=new_available_tokens,
                last_used_tokens=usage_delta,
                total_used_tokens=new_total_used_tokens,
            ),
        )
        if not updated:
            raise RuntimeError(f"Failed to apply usage delta for user {user_id}")
        return updated

    async def apply_token_usage_snapshot(
        self,
        user_id: int,
        token_usage_update: UserBillingUpdate,
    ) -> UserBilling:
        """Persist the cached token snapshot as the latest DB token state."""
        await self.get_orm_for_update(user_id=user_id)
        updated = await self.update_by_user_id(
            user_id=user_id,
            user_billing_update=token_usage_update,
        )
        if not updated:
            raise RuntimeError(
                f"Failed to apply token usage snapshot for user {user_id}"
            )
        return updated
