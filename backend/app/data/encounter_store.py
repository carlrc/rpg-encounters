from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.data.base_store import BaseStore
from app.db.models.character import CharacterORM
from app.db.models.encounter import EncounterORM
from app.models.encounter import Encounter, EncounterCreate, EncounterUpdate


class EncounterStore(BaseStore):
    def __init__(
        self,
        user_id: int,
        world_id: int,
        session: AsyncSession = None,
    ):
        super().__init__(user_id=user_id, world_id=world_id, session=session)

    async def get_all(self) -> List[Encounter]:
        """Get all encounters for the current user and world"""
        async with self.get_session() as session:
            result = await session.execute(
                select(EncounterORM)
                .options(selectinload(EncounterORM.characters))
                .where(
                    EncounterORM.user_id == self.user_id,
                    EncounterORM.world_id == self.world_id,
                )
            )
            encounter_orms = result.scalars().all()
            return [
                self._orm_to_encounter(encounter_orm)
                for encounter_orm in encounter_orms
            ]

    async def get_by_id(self, encounter_id: int) -> Encounter | None:
        """Get a specific encounter by ID for the current user and world"""
        async with self.get_session() as session:
            result = await session.execute(
                select(EncounterORM)
                .options(selectinload(EncounterORM.characters))
                .where(
                    EncounterORM.id == encounter_id,
                    EncounterORM.user_id == self.user_id,
                    EncounterORM.world_id == self.world_id,
                )
            )
            encounter_orm = result.scalars().first()
            if encounter_orm:
                return self._orm_to_encounter(encounter_orm)
            return None

    async def create(self, encounter_data: EncounterCreate) -> Encounter:
        """Create a new encounter"""
        async with self.get_session() as session:
            # Create the encounter without character_ids - much cleaner!
            encounter_dict = encounter_data.model_dump(exclude={"character_ids"})
            encounter_orm = EncounterORM(
                **encounter_dict, user_id=self.user_id, world_id=self.world_id
            )

            # Automatic association handling - always set characters to avoid lazy loading
            if encounter_data.character_ids:
                result = await session.execute(
                    select(CharacterORM).where(
                        CharacterORM.id.in_(encounter_data.character_ids)
                    )
                )
                characters = result.scalars().all()
                encounter_orm.characters = characters
            else:
                encounter_orm.characters = []  # Set empty list to avoid lazy loading

            session.add(encounter_orm)
            await session.flush()
            # No need to refresh since we already have the relationships loaded
            return self._orm_to_encounter(encounter_orm)

    async def update(
        self, encounter_id: int, encounter_update: EncounterUpdate
    ) -> Encounter | None:
        """Update an existing encounter"""
        async with self.get_session() as session:
            result = await session.execute(
                select(EncounterORM)
                .options(selectinload(EncounterORM.characters))
                .where(
                    EncounterORM.id == encounter_id,
                    EncounterORM.user_id == self.user_id,
                    EncounterORM.world_id == self.world_id,
                )
            )
            encounter_orm = result.scalars().first()

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
                result = await session.execute(
                    select(CharacterORM).where(
                        CharacterORM.id.in_(encounter_update.character_ids)
                    )
                )
                characters = result.scalars().all()
                encounter_orm.characters = characters

            await session.flush()
            await session.refresh(encounter_orm)
            return self._orm_to_encounter(encounter_orm)

    async def delete(self, encounter_id: int) -> bool:
        """Delete an encounter"""
        async with self.get_session() as session:
            result = await session.execute(
                select(EncounterORM).where(
                    EncounterORM.id == encounter_id,
                    EncounterORM.user_id == self.user_id,
                    EncounterORM.world_id == self.world_id,
                )
            )
            encounter_orm = result.scalars().first()
            if not encounter_orm:
                return False

            await session.delete(encounter_orm)
            return True

    async def add_character_to_encounter(
        self, encounter_id: int, character_id: int
    ) -> bool:
        """Add a character to an encounter if not already present"""
        async with self.get_session() as session:
            result = await session.execute(
                select(EncounterORM)
                .options(selectinload(EncounterORM.characters))
                .where(
                    EncounterORM.id == encounter_id,
                    EncounterORM.user_id == self.user_id,
                    EncounterORM.world_id == self.world_id,
                )
            )
            encounter_orm = result.scalars().first()

            if not encounter_orm:
                return False

            # Check if character is already in encounter
            current_character_ids = [char.id for char in encounter_orm.characters]
            if character_id in current_character_ids:
                return True  # Already present

            # Get the character ORM object and add to relationship
            result = await session.execute(
                select(CharacterORM).where(
                    CharacterORM.id == character_id,
                    CharacterORM.user_id == self.user_id,
                    CharacterORM.world_id == self.world_id,
                )
            )
            character_orm = result.scalars().first()

            if not character_orm:
                return False

            encounter_orm.characters.append(character_orm)
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
