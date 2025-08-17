from typing import List

from sqlalchemy.orm import sessionmaker

from app.db.connection import DB_ENGINE
from app.db.models.influence import InfluenceORM
from app.models.influence import Influence


class InfluenceStore:
    def __init__(self):
        self.Session = sessionmaker(DB_ENGINE)

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
                return self._orm_to_influence(influence_orm)

            # Create new influence
            new_influence = InfluenceORM(
                character_id=character_id, player_id=player_id, base=base, earned=0
            )
            session.add(new_influence)
            session.flush()  # Ensure entity is created before commit
            session.commit()
            session.refresh(new_influence)
            return self._orm_to_influence(new_influence)

    def update_influence(self, influence: Influence) -> Influence:
        """Update an existing influence state"""
        with self.Session() as session:
            influence_orm = (
                session.query(InfluenceORM)
                .filter(
                    InfluenceORM.character_id == influence.character_id,
                    InfluenceORM.player_id == influence.player_id,
                )
                .first()
            )

            if not influence_orm:
                # Create if doesn't exist
                influence_orm = InfluenceORM(
                    character_id=influence.character_id,
                    player_id=influence.player_id,
                    base=influence.base,
                    earned=influence.earned,
                )
                session.add(influence_orm)
            else:
                # Update existing
                influence_orm.base = influence.base
                influence_orm.earned = influence.earned

            session.commit()
            session.refresh(influence_orm)
            return self._orm_to_influence(influence_orm)

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
                return self._orm_to_influence(influence_orm)
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
            return [self._orm_to_influence(orm) for orm in influence_orms]

    def get_by_character_id(self, character_id: int) -> List[Influence]:
        """Get all influence records for a character"""
        with self.Session() as session:
            influence_orms = (
                session.query(InfluenceORM)
                .filter(InfluenceORM.character_id == character_id)
                .all()
            )
            return [self._orm_to_influence(orm) for orm in influence_orms]

    def get_by_player_id(self, player_id: int) -> List[Influence]:
        """Get all influence records for a player"""
        with self.Session() as session:
            influence_orms = (
                session.query(InfluenceORM)
                .filter(InfluenceORM.player_id == player_id)
                .all()
            )
            return [self._orm_to_influence(orm) for orm in influence_orms]

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

    def _orm_to_influence(self, influence_orm: InfluenceORM) -> Influence:
        """Convert InfluenceORM to Influence model"""
        return Influence(
            character_id=influence_orm.character_id,
            player_id=influence_orm.player_id,
            base=influence_orm.base,
            earned=influence_orm.earned,
        )
