from typing import List

from sqlalchemy.orm import sessionmaker

from app.db.connection import DB_ENGINE
from app.db.models.character import CharacterORM
from app.models.character import Character, CharacterCreate, CharacterUpdate


class CharacterStore:
    def __init__(self):
        self.Session = sessionmaker(DB_ENGINE)

    def get_all_characters(self) -> List[Character]:
        """Get all characters"""
        with self.Session() as session:
            character_orms = session.query(CharacterORM).all()
            return [
                Character.model_validate(character_orm)
                for character_orm in character_orms
            ]

    def get_character_by_id(self, character_id: int) -> Character | None:
        """Get a specific character by ID"""
        with self.Session() as session:
            character_orm = (
                session.query(CharacterORM)
                .filter(CharacterORM.id == character_id)
                .first()
            )
            if character_orm:
                return Character.model_validate(character_orm)
            return None

    def create_character(self, character_data: CharacterCreate) -> Character:
        """Create a new character"""
        with self.Session() as session:
            character_orm = CharacterORM(**character_data.model_dump())
            session.add(character_orm)
            session.commit()
            session.refresh(character_orm)
            return Character.model_validate(character_orm)

    def update_character(
        self, character_id: int, character_update: CharacterUpdate
    ) -> Character | None:
        """Update an existing character"""
        with self.Session() as session:
            character_orm = (
                session.query(CharacterORM)
                .filter(CharacterORM.id == character_id)
                .first()
            )
            if not character_orm:
                return None

            update_data = character_update.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                setattr(character_orm, key, value)

            session.commit()
            session.refresh(character_orm)
            return Character.model_validate(character_orm)

    def delete_character(self, character_id: int) -> bool:
        """Delete a character"""
        with self.Session() as session:
            character_orm = (
                session.query(CharacterORM)
                .filter(CharacterORM.id == character_id)
                .first()
            )
            if not character_orm:
                return False

            session.delete(character_orm)
            session.commit()
            return True

    def character_exists(self, character_id: int) -> bool:
        """Check if a character exists"""
        with self.Session() as session:
            return (
                session.query(CharacterORM)
                .filter(CharacterORM.id == character_id)
                .first()
                is not None
            )
