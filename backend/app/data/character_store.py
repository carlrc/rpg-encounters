from typing import List

from sqlalchemy import Engine

from app.data.base_store import BaseStore
from app.db.connection import get_db_engine
from app.db.models.character import CharacterORM
from app.models.character import Character, CharacterCreate, CharacterUpdate


class CharacterStore(BaseStore):
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

    def get_all_characters(self) -> List[Character]:
        """Get all characters for the current user and world"""
        with self.get_session() as session:
            character_orms = (
                session.query(CharacterORM)
                .filter(
                    CharacterORM.user_id == self.user_id,
                    CharacterORM.world_id == self.world_id,
                )
                .all()
            )
            return [
                Character.model_validate(character_orm)
                for character_orm in character_orms
            ]

    def get_character_by_id(self, character_id: int) -> Character | None:
        """Get a specific character by ID for the current user and world"""
        with self.get_session() as session:
            character_orm = (
                session.query(CharacterORM)
                .filter(
                    CharacterORM.id == character_id,
                    CharacterORM.user_id == self.user_id,
                    CharacterORM.world_id == self.world_id,
                )
                .first()
            )
            if character_orm:
                return Character.model_validate(character_orm)
            return None

    def create_character(self, character_data: CharacterCreate) -> Character:
        """Create a new character"""
        with self.get_session() as session:
            character_orm = CharacterORM(
                **character_data.model_dump(),
                user_id=self.user_id,
                world_id=self.world_id
            )
            session.add(character_orm)
            session.flush()
            session.refresh(character_orm)
            return Character.model_validate(character_orm)

    def update_character(
        self, character_id: int, character_update: CharacterUpdate
    ) -> Character | None:
        """Update an existing character for the current user and world"""
        with self.get_session() as session:
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
                return None

            update_data = character_update.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                setattr(character_orm, key, value)

            session.flush()
            session.refresh(character_orm)
            return Character.model_validate(character_orm)

    def delete_character(self, character_id: int) -> bool:
        """Delete a character for the current user and world"""
        with self.get_session() as session:
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

            session.delete(character_orm)
            return True

    def character_exists(self, character_id: int) -> bool:
        """Check if a character exists for the current user and world"""
        with self.get_session() as session:
            return (
                session.query(CharacterORM)
                .filter(
                    CharacterORM.id == character_id,
                    CharacterORM.user_id == self.user_id,
                    CharacterORM.world_id == self.world_id,
                )
                .first()
                is not None
            )
