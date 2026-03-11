import logging
from typing import List

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.data.base_store import BaseStore
from app.db.models.associations import encounter_players
from app.db.models.character import CharacterORM
from app.db.models.encounter import EncounterORM
from app.db.models.player import PlayerORM
from app.models.encounter import Encounter, EncounterCreate, EncounterUpdate

logger = logging.getLogger(__name__)


class EncounterStore(BaseStore):
    def __init__(
        self,
        user_id: int,
        world_id: int,
        session: AsyncSession | None = None,
    ):
        super().__init__(user_id=user_id, world_id=world_id, session=session)

    async def get_all(self) -> List[Encounter]:
        """Get all encounters for the current user and world"""
        try:
            async with self.get_session() as session:
                result = await session.execute(
                    select(EncounterORM)
                    .options(
                        selectinload(EncounterORM.characters),
                        selectinload(EncounterORM.players),
                    )
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
        except SQLAlchemyError as e:
            logger.error(
                f"Error in get_all for user {self.user_id}, world {self.world_id}: {e}"
            )
            raise

    async def get_by_id(self, encounter_id: int) -> Encounter | None:
        """Get a specific encounter by ID for the current user and world"""
        try:
            async with self.get_session() as session:
                result = await session.execute(
                    select(EncounterORM)
                    .options(
                        selectinload(EncounterORM.characters),
                        selectinload(EncounterORM.players),
                    )
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
        except SQLAlchemyError as e:
            logger.error(
                f"Error in get_by_id for user {self.user_id}, world {self.world_id}, encounter {encounter_id}: {e}"
            )
            raise

    async def create(self, encounter_data: EncounterCreate) -> Encounter | None:
        """Create a new encounter"""
        try:
            async with self.get_session() as session:
                # Create the encounter without character_ids at first
                encounter_dict = encounter_data.model_dump(
                    exclude={"character_ids", "player_ids"}
                )
                encounter_orm = EncounterORM(
                    **encounter_dict, user_id=self.user_id, world_id=self.world_id
                )

                # Automatic association handling - always set characters to avoid lazy loading
                if encounter_data.character_ids:
                    requested_character_ids = encounter_data.character_ids
                    # Use a set only for the existence check to avoid false negatives when the input list contains duplicates.
                    unique_character_ids = set(requested_character_ids)
                    result = await session.execute(
                        select(CharacterORM).where(
                            CharacterORM.id.in_(requested_character_ids),
                            CharacterORM.user_id == self.user_id,
                            CharacterORM.world_id == self.world_id,
                        )
                    )
                    characters = result.scalars().all()
                    # If any requested IDs are out-of-scope (other user/world, deleted, or invalid),
                    # the scoped query will return fewer rows. Treat as not found to avoid leaking.
                    if len(characters) != len(unique_character_ids):
                        logger.warning(
                            "Encounter create rejected: character IDs out of scope "
                            f"(user={self.user_id}, world={self.world_id}, "
                            f"requested={requested_character_ids})"
                        )
                        return None
                    encounter_orm.characters = characters
                else:
                    encounter_orm.characters = (
                        []
                    )  # Set empty list to avoid lazy loading

                if encounter_data.player_ids:
                    requested_player_ids = encounter_data.player_ids
                    # Use a set only for the existence check to avoid false negatives when the input list contains duplicates.
                    unique_player_ids = set(requested_player_ids)
                    result = await session.execute(
                        select(PlayerORM).where(
                            PlayerORM.id.in_(requested_player_ids),
                            PlayerORM.user_id == self.user_id,
                            PlayerORM.world_id == self.world_id,
                        )
                    )
                    players = result.scalars().all()
                    # If any requested IDs are out-of-scope (other user/world, deleted, or invalid),
                    # the scoped query will return fewer rows. Treat as not found to avoid leaking.
                    if len(players) != len(unique_player_ids):
                        logger.warning(
                            "Encounter create rejected: player IDs out of scope "
                            f"(user={self.user_id}, world={self.world_id}, "
                            f"requested={requested_player_ids})"
                        )
                        return None
                    encounter_orm.players = players
                else:
                    encounter_orm.players = []

                session.add(encounter_orm)
                await session.flush()
                # No need to refresh since we already have the relationships loaded
                return self._orm_to_encounter(encounter_orm)
        except SQLAlchemyError as e:
            logger.error(
                f"Error in create for user {self.user_id}, world {self.world_id}: {e}"
            )
            raise

    async def update(
        self, encounter_id: int, encounter_update: EncounterUpdate
    ) -> Encounter | None:
        """Update an existing encounter"""
        try:
            async with self.get_session() as session:
                result = await session.execute(
                    select(EncounterORM)
                    .options(
                        selectinload(EncounterORM.characters),
                        selectinload(EncounterORM.players),
                    )
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
                    exclude={"character_ids", "player_ids"}, exclude_unset=True
                )
                for key, value in update_data.items():
                    setattr(encounter_orm, key, value)

                # Update character relationships
                if encounter_update.character_ids is not None:
                    requested_character_ids = encounter_update.character_ids
                    # Use a set only for the existence check to avoid false negatives when the input list contains duplicates.
                    unique_character_ids = set(requested_character_ids)
                    result = await session.execute(
                        select(CharacterORM).where(
                            CharacterORM.id.in_(requested_character_ids),
                            CharacterORM.user_id == self.user_id,
                            CharacterORM.world_id == self.world_id,
                        )
                    )
                    characters = result.scalars().all()
                    # If any requested IDs are out-of-scope (other user/world, deleted, or invalid),
                    # the scoped query will return fewer rows. Treat as not found to avoid leaking.
                    if len(characters) != len(unique_character_ids):
                        logger.warning(
                            "Encounter update rejected: character IDs out of scope "
                            f"(user={self.user_id}, world={self.world_id}, "
                            f"requested={requested_character_ids})"
                        )
                        return None
                    encounter_orm.characters = characters

                # Update player relationships
                if encounter_update.player_ids is not None:
                    requested_player_ids = encounter_update.player_ids
                    # Use a set only for the existence check to avoid false negatives when the input list contains duplicates.
                    unique_player_ids = set(requested_player_ids)
                    result = await session.execute(
                        select(PlayerORM).where(
                            PlayerORM.id.in_(requested_player_ids),
                            PlayerORM.user_id == self.user_id,
                            PlayerORM.world_id == self.world_id,
                        )
                    )
                    players = result.scalars().all()
                    # If any requested IDs are out-of-scope (other user/world, deleted, or invalid),
                    # the scoped query will return fewer rows. Treat as not found to avoid leaking.
                    if len(players) != len(unique_player_ids):
                        logger.warning(
                            "Encounter update rejected: player IDs out of scope "
                            f"(user={self.user_id}, world={self.world_id}, "
                            f"requested={requested_player_ids})"
                        )
                        return None
                    encounter_orm.players = players

                await session.flush()
                await session.refresh(encounter_orm)
                return self._orm_to_encounter(encounter_orm)
        except SQLAlchemyError as e:
            logger.error(
                f"Error in update for user {self.user_id}, world {self.world_id}, encounter {encounter_id}: {e}"
            )
            raise

    async def delete(self, encounter_id: int) -> bool:
        """Delete an encounter"""
        try:
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
        except SQLAlchemyError as e:
            logger.error(
                f"Error in delete for user {self.user_id}, world {self.world_id}, encounter {encounter_id}: {e}"
            )
            raise

    async def add_character_to_encounter(
        self, encounter_id: int, character_id: int
    ) -> bool:
        """Add a character to an encounter if not already present"""
        try:
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
        except SQLAlchemyError as e:
            logger.error(
                f"Error in add_character_to_encounter for user {self.user_id}, world {self.world_id}, encounter {encounter_id}, character {character_id}: {e}"
            )
            raise

    async def get_by_player(self, player_id: int) -> Encounter | None:
        """Get the encounter assigned to a specific player"""
        try:
            async with self.get_session() as session:
                result = await session.execute(
                    select(EncounterORM)
                    .options(
                        selectinload(EncounterORM.characters),
                        selectinload(EncounterORM.players),
                    )
                    .join(encounter_players)
                    .where(
                        encounter_players.c.player_id == player_id,
                        EncounterORM.user_id == self.user_id,
                        EncounterORM.world_id == self.world_id,
                    )
                )
                encounter_orm = result.scalars().first()
                if encounter_orm:
                    return self._orm_to_encounter(encounter_orm)
                return None
        except SQLAlchemyError as e:
            logger.error(
                f"Error in get_by_player for user {self.user_id}, world {self.world_id}, player {player_id}: {e}"
            )
            raise

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
            player_ids=[player.id for player in encounter_orm.players],
        )
