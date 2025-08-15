from typing import List

from sqlalchemy.orm import sessionmaker

from app.db.connection import DB_ENGINE
from app.db.models.character import CharacterORM
from app.db.models.reveal import RevealORM
from app.models.reveal import Reveal, RevealCreate, RevealUpdate


class RevealStore:
    def __init__(self):
        self.Session = sessionmaker(DB_ENGINE)

    def get_all_reveals(self) -> List[Reveal]:
        """Get all reveals across all characters"""
        with self.Session() as session:
            reveal_orms = session.query(RevealORM).all()
            return [self._orm_to_reveal(reveal_orm) for reveal_orm in reveal_orms]

    def get_by_character_id(self, character_id: int) -> List[Reveal]:
        """Get all reveals for a character"""
        with self.Session() as session:
            reveal_orms = (
                session.query(RevealORM)
                .join(RevealORM.characters)
                .filter(CharacterORM.id == character_id)
                .all()
            )
            return [self._orm_to_reveal(reveal_orm) for reveal_orm in reveal_orms]

    def get_reveal(self, reveal_id: int) -> Reveal | None:
        """Get a specific reveal by ID"""
        with self.Session() as session:
            reveal_orm = (
                session.query(RevealORM).filter(RevealORM.id == reveal_id).first()
            )
            if reveal_orm:
                return self._orm_to_reveal(reveal_orm)
            return None

    def get_by_id(self, reveal_id: int) -> Reveal | None:
        """Get a specific reveal by ID (alias for get_reveal)"""
        return self.get_reveal(reveal_id)

    def create_reveal(self, reveal_data: RevealCreate) -> Reveal:
        """Create a new reveal"""
        with self.Session() as session:
            # Create the reveal without character_ids
            reveal_dict = reveal_data.model_dump(exclude={"character_ids"})
            reveal_orm = RevealORM(**reveal_dict)
            session.add(reveal_orm)
            session.flush()  # Ensure entities are created for many-to-many

            # Add character associations
            if reveal_data.character_ids:
                characters = (
                    session.query(CharacterORM)
                    .filter(CharacterORM.id.in_(reveal_data.character_ids))
                    .all()
                )
                reveal_orm.characters = characters

            session.commit()
            session.refresh(reveal_orm)
            return self._orm_to_reveal(reveal_orm)

    def update_reveal(
        self, reveal_id: int, reveal_update: RevealUpdate
    ) -> Reveal | None:
        """Update an existing reveal"""
        with self.Session() as session:
            reveal_orm = (
                session.query(RevealORM).filter(RevealORM.id == reveal_id).first()
            )
            if not reveal_orm:
                return None

            # Update basic fields
            update_data = reveal_update.model_dump(
                exclude={"character_ids"}, exclude_unset=True
            )
            for key, value in update_data.items():
                setattr(reveal_orm, key, value)

            # Update character associations if provided
            if (
                hasattr(reveal_update, "character_ids")
                and reveal_update.character_ids is not None
            ):
                characters = (
                    session.query(CharacterORM)
                    .filter(CharacterORM.id.in_(reveal_update.character_ids))
                    .all()
                )
                reveal_orm.characters = characters

            session.commit()
            session.refresh(reveal_orm)
            return self._orm_to_reveal(reveal_orm)

    def delete_reveal(self, reveal_id: int) -> bool:
        """Delete a reveal"""
        with self.Session() as session:
            reveal_orm = (
                session.query(RevealORM).filter(RevealORM.id == reveal_id).first()
            )
            if not reveal_orm:
                return False

            session.delete(reveal_orm)
            session.commit()
            return True

    def reveal_exists(self, reveal_id: int) -> bool:
        """Check if a reveal exists"""
        with self.Session() as session:
            return (
                session.query(RevealORM).filter(RevealORM.id == reveal_id).first()
                is not None
            )

    def _orm_to_reveal(self, reveal_orm: RevealORM) -> Reveal:
        """Convert RevealORM to Reveal model"""
        return Reveal(
            id=reveal_orm.id,
            title=reveal_orm.title,
            character_ids=[char.id for char in reveal_orm.characters],
            level_1_content=reveal_orm.level_1_content,
            level_2_content=reveal_orm.level_2_content,
            level_3_content=reveal_orm.level_3_content,
            standard_threshold=reveal_orm.standard_threshold,
            privileged_threshold=reveal_orm.privileged_threshold,
            exclusive_threshold=reveal_orm.exclusive_threshold,
        )
