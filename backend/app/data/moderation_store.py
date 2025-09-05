import logging
from typing import List

from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.data.base_store import BaseStore
from app.db.models.moderation import ModerationORM
from app.models.moderation import Moderation, ModerationCreate, ModerationUpdate

logger = logging.getLogger(__name__)


class ModerationStore(BaseStore):
    def __init__(self, user_id: int, session: AsyncSession = None):
        super().__init__(user_id=user_id, world_id=None, session=session)

    async def create(self, moderation_data: ModerationCreate) -> Moderation:
        async with self.get_session() as session:
            db_moderation = ModerationORM(**moderation_data.model_dump())
            session.add(db_moderation)
            await session.flush()
            await session.refresh(db_moderation)
            return Moderation.model_validate(db_moderation)

    async def get_by_id(self, moderation_id: int) -> Moderation | None:
        async with self.get_session() as session:
            result = await session.execute(
                select(ModerationORM).where(ModerationORM.id == moderation_id)
            )
            moderation = result.scalar_one_or_none()
            return Moderation.model_validate(moderation) if moderation else None

    async def get_moderations_by_user_id(self, user_id: int) -> List[Moderation]:
        async with self.get_session() as session:
            result = await session.execute(
                select(ModerationORM)
                .where(ModerationORM.user_id == user_id)
                .order_by(ModerationORM.created_at.desc())
            )
            moderations = result.scalars().all()
            return [Moderation.model_validate(moderation) for moderation in moderations]

    async def get_all(self) -> List[Moderation]:
        async with self.get_session() as session:
            result = await session.execute(
                select(ModerationORM).order_by(ModerationORM.created_at.desc())
            )
            moderations = result.scalars().all()
            return [Moderation.model_validate(moderation) for moderation in moderations]

    async def update(
        self, moderation_id: int, moderation_update: ModerationUpdate
    ) -> Moderation | None:
        update_data = moderation_update.model_dump(exclude_unset=True)
        if not update_data:
            return await self.get_by_id(moderation_id)

        async with self.get_session() as session:
            await session.execute(
                update(ModerationORM)
                .where(ModerationORM.id == moderation_id)
                .values(**update_data)
            )
        return await self.get_by_id(moderation_id)

    async def delete(self, moderation_id: int) -> bool:
        async with self.get_session() as session:
            result = await session.execute(
                delete(ModerationORM).where(ModerationORM.id == moderation_id)
            )
            return result.rowcount > 0

    async def exists(self, moderation_id: int) -> bool:
        async with self.get_session() as session:
            result = await session.execute(
                select(ModerationORM.id).where(ModerationORM.id == moderation_id)
            )
            return result.scalar_one_or_none() is not None
