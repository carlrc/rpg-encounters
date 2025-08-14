from typing import List

from app.models.encounter import Encounter, EncounterCreate, EncounterUpdate
from tests.fixtures.encounters import encounters_db, next_encounter_id


class EncounterStore:
    def __init__(self):
        self.encounters = encounters_db
        self.next_id = next_encounter_id

    def get_all_encounters(self) -> List[Encounter]:
        """Get all encounters"""
        return list(self.encounters.values())

    def get_encounter_by_id(self, encounter_id: int) -> Encounter | None:
        """Get a specific encounter by ID"""
        return self.encounters.get(encounter_id)

    def create_encounter(self, encounter_data: EncounterCreate) -> Encounter:
        """Create a new encounter"""
        encounter_dict = encounter_data.model_dump()
        encounter_dict["id"] = self.next_id

        new_encounter = Encounter(**encounter_dict)
        self.encounters[self.next_id] = new_encounter
        self.next_id += 1

        return new_encounter

    def update_encounter(
        self, encounter_id: int, encounter_update: EncounterUpdate
    ) -> Encounter | None:
        """Update an existing encounter"""
        if encounter_id not in self.encounters:
            return None

        existing_encounter = self.encounters[encounter_id]
        update_data = encounter_update.model_dump(exclude_unset=True)

        # Update the existing encounter with new data
        updated_data = existing_encounter.model_dump()
        updated_data.update(update_data)

        updated_encounter = Encounter(**updated_data)
        self.encounters[encounter_id] = updated_encounter

        return updated_encounter

    def delete_encounter(self, encounter_id: int) -> bool:
        """Delete an encounter"""
        if encounter_id not in self.encounters:
            return False

        del self.encounters[encounter_id]
        return True
