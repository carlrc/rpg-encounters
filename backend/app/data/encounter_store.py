from typing import List

from sqlalchemy.orm import sessionmaker

from app.db.connection import get_db_engine
from app.db.models.character import CharacterORM
from app.db.models.encounter import EncounterORM
from app.models.encounter import Encounter, EncounterCreate, EncounterUpdate


class EncounterStore:
    def __init__(self):
        self.Session = sessionmaker(get_db_engine())

    def get_all_encounters(self) -> List[Encounter]:
        """Get all encounters"""
        with self.Session() as session:
            encounter_orms = session.query(EncounterORM).all()
            return [
                self._orm_to_encounter(encounter_orm)
                for encounter_orm in encounter_orms
            ]

    def get_encounter_by_id(self, encounter_id: int) -> Encounter | None:
        """Get a specific encounter by ID"""
        with self.Session() as session:
            encounter_orm = (
                session.query(EncounterORM)
                .filter(EncounterORM.id == encounter_id)
                .first()
            )
            if encounter_orm:
                return self._orm_to_encounter(encounter_orm)
            return None

    def create_encounter(self, encounter_data: EncounterCreate) -> Encounter:
        """Create a new encounter"""
        with self.Session() as session:
            # Create the encounter without character_ids
            encounter_dict = encounter_data.model_dump(exclude={"character_ids"})
            encounter_orm = EncounterORM(**encounter_dict)
            session.add(encounter_orm)
            session.flush()  # Ensure entities are created for many-to-many

            # Add character associations
            if encounter_data.character_ids:
                characters = (
                    session.query(CharacterORM)
                    .filter(CharacterORM.id.in_(encounter_data.character_ids))
                    .all()
                )
                encounter_orm.characters = characters

            session.commit()
            session.refresh(encounter_orm)
            return self._orm_to_encounter(encounter_orm)

    def update_encounter(
        self, encounter_id: int, encounter_update: EncounterUpdate
    ) -> Encounter | None:
        """Update an existing encounter"""
        with self.Session() as session:
            encounter_orm = (
                session.query(EncounterORM)
                .filter(EncounterORM.id == encounter_id)
                .first()
            )
            if not encounter_orm:
                return None

            # Update basic fields
            update_data = encounter_update.model_dump(
                exclude={"character_ids"}, exclude_unset=True
            )
            for key, value in update_data.items():
                setattr(encounter_orm, key, value)

            # Update character associations if provided
            if (
                hasattr(encounter_update, "character_ids")
                and encounter_update.character_ids is not None
            ):
                characters = (
                    session.query(CharacterORM)
                    .filter(CharacterORM.id.in_(encounter_update.character_ids))
                    .all()
                )
                encounter_orm.characters = characters

            session.commit()
            session.refresh(encounter_orm)
            return self._orm_to_encounter(encounter_orm)

    def delete_encounter(self, encounter_id: int) -> bool:
        """Delete an encounter"""
        with self.Session() as session:
            encounter_orm = (
                session.query(EncounterORM)
                .filter(EncounterORM.id == encounter_id)
                .first()
            )
            if not encounter_orm:
                return False

            session.delete(encounter_orm)
            session.commit()
            return True

    def _orm_to_encounter(self, encounter_orm: EncounterORM) -> Encounter:
        """Convert EncounterORM to Encounter model"""
        return Encounter(
            id=encounter_orm.id,
            name=encounter_orm.name,
            description=encounter_orm.description,
            position_x=encounter_orm.position_x,
            position_y=encounter_orm.position_y,
            character_ids=[char.id for char in encounter_orm.characters],
        )
