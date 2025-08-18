from typing import List

from sqlalchemy.orm import sessionmaker

from app.db.connection import get_db_engine
from app.db.models.influence import InfluenceORM
from app.models.influence import Influence


class InfluenceStore:
    def __init__(self, user_id: int, world_id: int):
        self.Session = sessionmaker(get_db_engine())
        self.user_id = user_id
        self.world_id = world_id

    def get_or_create(
        self, character_id: int, player_id: int, base: int = 0
    ) -> Influence:
        """Get existing influence state or create new one"""
        with self.Session() as session:
            influence_orm = (
                session.query(InfluenceORM)
                .filter(
                    InfluenceORM.character_id == character_id,
                    InfluenceORM.player_id == player_id,
                )
                .first()
            )

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
            session.flush()  # Ensure entity is created before commit
            session.commit()
            session.refresh(new_influence)
            return Influence.model_validate(new_influence)

    def update_influence(self, influence: Influence) -> Influence | None:
        """Update existing influence"""
        with self.Session() as session:
            influence_orm = (
                session.query(InfluenceORM)
                .filter(
                    InfluenceORM.character_id == influence.character_id,
                    InfluenceORM.player_id == influence.player_id,
                    InfluenceORM.user_id == self.user_id,
                    InfluenceORM.world_id == self.world_id,
                )
                .first()
            )

            if not influence_orm:
                return None

            # Only update existing records
            influence_orm.base = influence.base
            influence_orm.earned = influence.earned

            session.commit()
            session.refresh(influence_orm)
            return Influence.model_validate(influence_orm)

    def create_influence(self, influence: Influence) -> Influence:
        """Separate method for creating new influence records"""
        with self.Session() as session:
            influence_orm = InfluenceORM(
                character_id=influence.character_id,
                player_id=influence.player_id,
                base=influence.base,
                earned=influence.earned,
                user_id=self.user_id,
                world_id=self.world_id,
            )
            session.add(influence_orm)
            session.commit()
            session.refresh(influence_orm)
            return Influence.model_validate(influence_orm)

    def get_influence(self, character_id: int, player_id: int) -> Influence | None:
        """Get influence state for character-player pair"""
        with self.Session() as session:
            influence_orm = (
                session.query(InfluenceORM)
                .filter(
                    InfluenceORM.character_id == character_id,
                    InfluenceORM.player_id == player_id,
                )
                .first()
            )

            if influence_orm:
                return Influence.model_validate(influence_orm)
            return None

    def reset_influence(self, character_id: int, player_id: int) -> bool:
        """Reset earned influence to 0, keep base influence"""
        with self.Session() as session:
            influence_orm = (
                session.query(InfluenceORM)
                .filter(
                    InfluenceORM.character_id == character_id,
                    InfluenceORM.player_id == player_id,
                )
                .first()
            )

            if influence_orm:
                influence_orm.earned = 0
                session.commit()
                return True
            return False

    def get_all_influences(self) -> List[Influence]:
        """Get all influence records"""
        with self.Session() as session:
            influence_orms = session.query(InfluenceORM).all()
            return [Influence.model_validate(orm) for orm in influence_orms]

    def get_by_character_id(self, character_id: int) -> List[Influence]:
        """Get all influence records for a character"""
        with self.Session() as session:
            influence_orms = (
                session.query(InfluenceORM)
                .filter(InfluenceORM.character_id == character_id)
                .all()
            )
            return [Influence.model_validate(orm) for orm in influence_orms]

    def get_by_player_id(self, player_id: int) -> List[Influence]:
        """Get all influence records for a player"""
        with self.Session() as session:
            influence_orms = (
                session.query(InfluenceORM)
                .filter(InfluenceORM.player_id == player_id)
                .all()
            )
            return [Influence.model_validate(orm) for orm in influence_orms]

    def delete_influence(self, character_id: int, player_id: int) -> bool:
        """Delete an influence record"""
        with self.Session() as session:
            influence_orm = (
                session.query(InfluenceORM)
                .filter(
                    InfluenceORM.character_id == character_id,
                    InfluenceORM.player_id == player_id,
                )
                .first()
            )

            if not influence_orm:
                return False

            session.delete(influence_orm)
            session.commit()
            return True

    def clear(self) -> None:
        """Clear all influence states - used for testing"""
        with self.Session() as session:
            session.query(InfluenceORM).delete()
            session.commit()
