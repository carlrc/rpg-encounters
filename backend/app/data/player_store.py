from typing import List

from sqlalchemy.orm import sessionmaker

from app.db.connection import DB_ENGINE
from app.db.models.player import PlayerORM
from app.models.player import Player, PlayerCreate, PlayerUpdate


class PlayerStore:
    def __init__(self):
        self.Session = sessionmaker(DB_ENGINE)

    def get_all_players(self) -> List[Player]:
        """Get all players"""
        with self.Session() as session:
            player_orms = session.query(PlayerORM).all()
            return [Player.model_validate(player_orm) for player_orm in player_orms]

    def get_player_by_id(self, player_id: int) -> Player | None:
        """Get a specific player by ID"""
        with self.Session() as session:
            player_orm = (
                session.query(PlayerORM).filter(PlayerORM.id == player_id).first()
            )
            if player_orm:
                return Player.model_validate(player_orm)
            return None

    def create_player(self, player_data: PlayerCreate) -> Player:
        """Create a new player"""
        with self.Session() as session:
            player_orm = PlayerORM(**player_data.model_dump())
            session.add(player_orm)
            session.commit()
            session.refresh(player_orm)
            return Player.model_validate(player_orm)

    def update_player(
        self, player_id: int, player_update: PlayerUpdate
    ) -> Player | None:
        """Update an existing player"""
        with self.Session() as session:
            player_orm = (
                session.query(PlayerORM).filter(PlayerORM.id == player_id).first()
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
        """Delete a player"""
        with self.Session() as session:
            player_orm = (
                session.query(PlayerORM).filter(PlayerORM.id == player_id).first()
            )
            if not player_orm:
                return False

            session.delete(player_orm)
            session.commit()
            return True

    def player_exists(self, player_id: int) -> bool:
        """Check if a player exists"""
        with self.Session() as session:
            return (
                session.query(PlayerORM).filter(PlayerORM.id == player_id).first()
                is not None
            )
