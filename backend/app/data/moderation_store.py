import logging
from typing import List, Optional

from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.data.base_store import BaseStore
from app.db.models.moderation import ModerationORM
from app.models.moderation import Moderation, ModerationCreate, ModerationUpdate

logger = logging.getLogger(__name__)


class ModerationStore(BaseStore):
    def __init__(self, user_id: Optional[int] = None, session: AsyncSession = None):
        super().__init__(user_id, None, session)

    async def create_moderation(self, moderation_data: ModerationCreate) -> Moderation:
        db_moderation = ModerationORM(**moderation_data.model_dump())
        self.session.add(db_moderation)
        await self.session.flush()
        await self.session.refresh(db_moderation)
        return Moderation.model_validate(db_moderation)

    async def get_moderation_by_id(self, moderation_id: int) -> Optional[Moderation]:
        result = await self.session.execute(
            select(ModerationORM).where(ModerationORM.id == moderation_id)
        )
        moderation = result.scalar_one_or_none()
        return Moderation.model_validate(moderation) if moderation else None

    async def get_moderations_by_user_id(self, user_id: int) -> List[Moderation]:
        result = await self.session.execute(
            select(ModerationORM)
            .where(ModerationORM.user_id == user_id)
            .order_by(ModerationORM.created_at.desc())
        )
        moderations = result.scalars().all()
        return [Moderation.model_validate(moderation) for moderation in moderations]

    async def get_all_moderations(self) -> List[Moderation]:
        result = await self.session.execute(
            select(ModerationORM).order_by(ModerationORM.created_at.desc())
        )
        moderations = result.scalars().all()
        return [Moderation.model_validate(moderation) for moderation in moderations]

    async def update_moderation(
        self, moderation_id: int, moderation_update: ModerationUpdate
    ) -> Optional[Moderation]:
        update_data = moderation_update.model_dump(exclude_unset=True)
        if not update_data:
            return await self.get_moderation_by_id(moderation_id)

        await self.session.execute(
            update(ModerationORM)
            .where(ModerationORM.id == moderation_id)
            .values(**update_data)
        )
        return await self.get_moderation_by_id(moderation_id)

    async def delete_moderation(self, moderation_id: int) -> bool:
        result = await self.session.execute(
            delete(ModerationORM).where(ModerationORM.id == moderation_id)
        )
        return result.rowcount > 0

    async def moderation_exists(self, moderation_id: int) -> bool:
        result = await self.session.execute(
            select(ModerationORM.id).where(ModerationORM.id == moderation_id)
        )
        return result.scalar_one_or_none() is not None
