from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.data.base_store import BaseStore
from app.db.models.influence import InfluenceORM
from app.models.influence import Influence


class InfluenceStore(BaseStore):
    def __init__(
        self,
        user_id: int,
        world_id: int,
        session: AsyncSession = None,
    ):
        super().__init__(user_id=user_id, world_id=world_id, session=session)

    async def get_or_create_influence(
        self, character_id: int, player_id: int, base: int = 0
    ) -> Influence:
        """Get existing influence state or create new one"""
        async with self.get_session() as session:
            result = await session.execute(
                select(InfluenceORM).where(
                    InfluenceORM.character_id == character_id,
                    InfluenceORM.player_id == player_id,
                    InfluenceORM.user_id == self.user_id,
                    InfluenceORM.world_id == self.world_id,
                )
            )
            influence_orm = result.scalars().first()

            if influence_orm:
                return Influence.model_validate(influence_orm)

            # Create new influence
            new_influence = InfluenceORM(
                character_id=character_id,
                player_id=player_id,
                base=base,
                earned=0,
                user_id=self.user_id,
                world_id=self.world_id,
            )
            session.add(new_influence)
            await session.flush()
            await session.refresh(new_influence)
            return Influence.model_validate(new_influence)

    async def update(self, influence: Influence) -> Influence | None:
        """Update existing influence"""
        async with self.get_session() as session:
            result = await session.execute(
                select(InfluenceORM).where(
                    InfluenceORM.character_id == influence.character_id,
                    InfluenceORM.player_id == influence.player_id,
                    InfluenceORM.user_id == self.user_id,
                    InfluenceORM.world_id == self.world_id,
                )
            )
            influence_orm = result.scalars().first()

            if not influence_orm:
                return None

            # Only update existing records
            influence_orm.base = influence.base
            influence_orm.earned = influence.earned

            await session.flush()
            await session.refresh(influence_orm)
            return Influence.model_validate(influence_orm)

    async def create(self, influence: Influence) -> Influence:
        """Separate method for creating new influence records"""
        async with self.get_session() as session:
            influence_orm = InfluenceORM(
                character_id=influence.character_id,
                player_id=influence.player_id,
                base=influence.base,
                earned=influence.earned,
                user_id=self.user_id,
                world_id=self.world_id,
            )
            session.add(influence_orm)
            await session.flush()
            await session.refresh(influence_orm)
            return Influence.model_validate(influence_orm)

    async def get_influence(
        self, character_id: int, player_id: int
    ) -> Influence | None:
        """Get influence state for character-player pair"""
        async with self.get_session() as session:
            result = await session.execute(
                select(InfluenceORM).where(
                    InfluenceORM.character_id == character_id,
                    InfluenceORM.player_id == player_id,
                )
            )
            influence_orm = result.scalars().first()

            if influence_orm:
                return Influence.model_validate(influence_orm)
            return None

    async def reset_influence(self, character_id: int, player_id: int) -> bool:
        """Reset earned influence to 0, keep base influence"""
        async with self.get_session() as session:
            result = await session.execute(
                select(InfluenceORM).where(
                    InfluenceORM.character_id == character_id,
                    InfluenceORM.player_id == player_id,
                )
            )
            influence_orm = result.scalars().first()

            if influence_orm:
                influence_orm.earned = 0
                return True
            return False

    async def get_all(self) -> List[Influence]:
        """Get all influence records"""
        async with self.get_session() as session:
            result = await session.execute(select(InfluenceORM))
            influence_orms = result.scalars().all()
            return [Influence.model_validate(orm) for orm in influence_orms]

    async def get_by_character_id(self, character_id: int) -> List[Influence]:
        """Get all influence records for a character"""
        async with self.get_session() as session:
            result = await session.execute(
                select(InfluenceORM).where(InfluenceORM.character_id == character_id)
            )
            influence_orms = result.scalars().all()
            return [Influence.model_validate(orm) for orm in influence_orms]

    async def get_by_player_id(self, player_id: int) -> List[Influence]:
        """Get all influence records for a player"""
        async with self.get_session() as session:
            result = await session.execute(
                select(InfluenceORM).where(InfluenceORM.player_id == player_id)
            )
            influence_orms = result.scalars().all()
            return [Influence.model_validate(orm) for orm in influence_orms]

    async def delete(self, character_id: int, player_id: int) -> bool:
        """Delete an influence record"""
        async with self.get_session() as session:
            result = await session.execute(
                select(InfluenceORM).where(
                    InfluenceORM.character_id == character_id,
                    InfluenceORM.player_id == player_id,
                )
            )
            influence_orm = result.scalars().first()

            if not influence_orm:
                return False

            await session.delete(influence_orm)
            return True

    async def clear(self) -> None:
        """Clear all influence states - used for testing"""
        async with self.get_session() as session:
            result = await session.execute(select(InfluenceORM))
            influence_orms = result.scalars().all()
            for influence_orm in influence_orms:
                await session.delete(influence_orm)
