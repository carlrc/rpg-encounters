from typing import List

from sqlalchemy import Engine

from app.data.base_store import BaseStore
from app.db.connection import get_db_engine
from app.db.models.world import WorldORM
from app.models.world import World


class WorldStore(BaseStore):
    def __init__(self, user_id: int, engine: Engine = get_db_engine(), session=None):
        # WorldStore has user_id but no world_id, so we pass None for world_id
        super().__init__(user_id=user_id, world_id=None, engine=engine, session=session)

    def get_all_worlds(self) -> List[World]:
        """Get all worlds for the current user"""
        with self.get_session() as session:
            world_orms = (
                session.query(WorldORM)
                .filter(WorldORM.user_id == self.user_id)
                .order_by(WorldORM.created_at)
                .all()
            )
            return [World.model_validate(world_orm) for world_orm in world_orms]

    def get_world_by_id(self, world_id: int) -> World | None:
        """Get a specific world by ID for the current user"""
        with self.get_session() as session:
            world_orm = (
                session.query(WorldORM)
                .filter(WorldORM.id == world_id, WorldORM.user_id == self.user_id)
                .first()
            )
            if world_orm:
                return World.model_validate(world_orm)
            return None

    def create_world(self) -> World:
        """Create a new world for the current user"""
        with self.get_session() as session:
            # Create world with just user_id, other fields are auto-generated
            world_orm = WorldORM(user_id=self.user_id)
            session.add(world_orm)
            session.commit()
            session.refresh(world_orm)
            return World.model_validate(world_orm)

    def delete_world(self, world_id: int) -> bool:
        """Delete a world for the current user"""
        with self.get_session() as session:
            world_orm = (
                session.query(WorldORM)
                .filter(WorldORM.id == world_id, WorldORM.user_id == self.user_id)
                .first()
            )
            if not world_orm:
                return False

            session.delete(world_orm)
            session.commit()
            return True

    def world_exists(self, world_id: int) -> bool:
        """Check if a world exists for the current user"""
        with self.get_session() as session:
            return (
                session.query(WorldORM)
                .filter(WorldORM.id == world_id, WorldORM.user_id == self.user_id)
                .first()
                is not None
            )
