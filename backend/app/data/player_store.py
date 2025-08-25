from typing import List

from sqlalchemy import Engine

from app.data.base_store import BaseStore
from app.db.connection import get_db_engine
from app.db.models.player import PlayerORM
from app.models.player import Player, PlayerCreate, PlayerUpdate


class PlayerStore(BaseStore):
    def __init__(
        self,
        user_id: int,
        world_id: int,
        engine: Engine = get_db_engine(),
        session=None,
    ):
        super().__init__(
            user_id=user_id, world_id=world_id, engine=engine, session=session
        )

    def get_all_players(self) -> List[Player]:
        """Get all players for the current user and world"""
        with self.get_session() as session:
            player_orms = (
                session.query(PlayerORM)
                .filter(
                    PlayerORM.user_id == self.user_id,
                    PlayerORM.world_id == self.world_id,
                )
                .all()
            )
            return [Player.model_validate(player_orm) for player_orm in player_orms]

    def get_player_by_id(self, player_id: int) -> Player | None:
        """Get a specific player by ID for the current user and world"""
        with self.get_session() as session:
            player_orm = (
                session.query(PlayerORM)
                .filter(
                    PlayerORM.id == player_id,
                    PlayerORM.user_id == self.user_id,
                    PlayerORM.world_id == self.world_id,
                )
                .first()
            )
            if player_orm:
                return Player.model_validate(player_orm)
            return None

    def create_player(self, player_data: PlayerCreate) -> Player:
        """Create a new player"""
        with self.get_session() as session:
            player_orm = PlayerORM(
                **player_data.model_dump(), user_id=self.user_id, world_id=self.world_id
            )
            session.add(player_orm)
            session.commit()
            session.refresh(player_orm)
            return Player.model_validate(player_orm)

    def update_player(
        self, player_id: int, player_update: PlayerUpdate
    ) -> Player | None:
        """Update an existing player for the current user and world"""
        with self.get_session() as session:
            player_orm = (
                session.query(PlayerORM)
                .filter(
                    PlayerORM.id == player_id,
                    PlayerORM.user_id == self.user_id,
                    PlayerORM.world_id == self.world_id,
                )
                .first()
            )
            if not player_orm:
                return None

            update_data = player_update.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                setattr(player_orm, key, value)

            session.commit()
            session.refresh(player_orm)
            return Player.model_validate(player_orm)

    def delete_player(self, player_id: int) -> bool:
        """Delete a player for the current user and world"""
        with self.get_session() as session:
            player_orm = (
                session.query(PlayerORM)
                .filter(
                    PlayerORM.id == player_id,
                    PlayerORM.user_id == self.user_id,
                    PlayerORM.world_id == self.world_id,
                )
                .first()
            )
            if not player_orm:
                return False

            session.delete(player_orm)
            session.commit()
            return True

    def player_exists(self, player_id: int) -> bool:
        """Check if a player exists for the current user and world"""
        with self.get_session() as session:
            return (
                session.query(PlayerORM)
                .filter(
                    PlayerORM.id == player_id,
                    PlayerORM.user_id == self.user_id,
                    PlayerORM.world_id == self.world_id,
                )
                .first()
                is not None
            )
