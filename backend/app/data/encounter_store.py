from typing import List

from sqlalchemy import Engine

from app.data.base_store import BaseStore
from app.db.connection import get_db_engine
from app.db.models.character import CharacterORM
from app.db.models.encounter import EncounterORM
from app.models.encounter import Encounter, EncounterCreate, EncounterUpdate


class EncounterStore(BaseStore):
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

    def get_all_encounters(self) -> List[Encounter]:
        """Get all encounters for the current user and world"""
        with self.get_session() as session:
            encounter_orms = (
                session.query(EncounterORM)
                .filter(
                    EncounterORM.user_id == self.user_id,
                    EncounterORM.world_id == self.world_id,
                )
                .all()
            )
            return [
                self._orm_to_encounter(encounter_orm)
                for encounter_orm in encounter_orms
            ]

    def get_encounter_by_id(self, encounter_id: int) -> Encounter | None:
        """Get a specific encounter by ID for the current user and world"""
        with self.get_session() as session:
            encounter_orm = (
                session.query(EncounterORM)
                .filter(
                    EncounterORM.id == encounter_id,
                    EncounterORM.user_id == self.user_id,
                    EncounterORM.world_id == self.world_id,
                )
                .first()
            )
            if encounter_orm:
                return self._orm_to_encounter(encounter_orm)
            return None

    def create_encounter(self, encounter_data: EncounterCreate) -> Encounter:
        """Create a new encounter"""
        with self.get_session() as session:
            # Create the encounter without character_ids - much cleaner!
            encounter_dict = encounter_data.model_dump(exclude={"character_ids"})
            encounter_orm = EncounterORM(
                **encounter_dict, user_id=self.user_id, world_id=self.world_id
            )

            # Automatic association handling
            if encounter_data.character_ids:
                characters = (
                    session.query(CharacterORM)
                    .filter(CharacterORM.id.in_(encounter_data.character_ids))
                    .all()
                )
                encounter_orm.characters = characters

            session.add(encounter_orm)
            session.commit()
            session.refresh(encounter_orm)
            return self._orm_to_encounter(encounter_orm)

    def update_encounter(
        self, encounter_id: int, encounter_update: EncounterUpdate
    ) -> Encounter | None:
        """Update an existing encounter"""
        with self.get_session() as session:
            encounter_orm = (
                session.query(EncounterORM)
                .filter(
                    EncounterORM.id == encounter_id,
                    EncounterORM.user_id == self.user_id,
                    EncounterORM.world_id == self.world_id,
                )
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

            # Update character relationships
            if encounter_update.character_ids is not None:
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
        with self.get_session() as session:
            encounter_orm = (
                session.query(EncounterORM)
                .filter(
                    EncounterORM.id == encounter_id,
                    EncounterORM.user_id == self.user_id,
                    EncounterORM.world_id == self.world_id,
                )
                .first()
            )
            if not encounter_orm:
                return False

            session.delete(encounter_orm)
            session.commit()
            return True

    def add_character_to_encounter(self, encounter_id: int, character_id: int) -> bool:
        """Add a character to an encounter if not already present"""
        with self.get_session() as session:
            encounter_orm = (
                session.query(EncounterORM)
                .filter(
                    EncounterORM.id == encounter_id,
                    EncounterORM.user_id == self.user_id,
                    EncounterORM.world_id == self.world_id,
                )
                .first()
            )

            if not encounter_orm:
                return False

            # Check if character is already in encounter
            current_character_ids = [char.id for char in encounter_orm.characters]
            if character_id in current_character_ids:
                return True  # Already present

            # Get the character ORM object and add to relationship
            character_orm = (
                session.query(CharacterORM)
                .filter(
                    CharacterORM.id == character_id,
                    CharacterORM.user_id == self.user_id,
                    CharacterORM.world_id == self.world_id,
                )
                .first()
            )

            if not character_orm:
                return False

            encounter_orm.characters.append(character_orm)
            session.flush()
            session.commit()
            return True

    def _orm_to_encounter(self, encounter_orm: EncounterORM) -> Encounter:
        """Convert EncounterORM to Encounter model"""
        return Encounter(
            id=encounter_orm.id,
            user_id=encounter_orm.user_id,
            world_id=encounter_orm.world_id,
            name=encounter_orm.name,
            description=encounter_orm.description,
            position_x=encounter_orm.position_x,
            position_y=encounter_orm.position_y,
            character_ids=[char.id for char in encounter_orm.characters],
        )
