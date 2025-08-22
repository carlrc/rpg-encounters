from typing import List

from sqlalchemy import Engine
from sqlalchemy.orm import sessionmaker

from app.db.connection import get_db_engine
from app.db.models.character import CharacterORM
from app.db.models.reveal import RevealORM
from app.models.reveal import Reveal, RevealCreate, RevealUpdate


class RevealStore:
    def __init__(self, user_id: int, world_id: int, engine: Engine = get_db_engine()):
        self.Session = sessionmaker(engine)
        self.user_id = user_id
        self.world_id = world_id

    def get_all_reveals(self) -> List[Reveal]:
        """Get all reveals for the current user and world"""
        with self.Session() as session:
            reveal_orms = (
                session.query(RevealORM)
                .filter(
                    RevealORM.user_id == self.user_id,
                    RevealORM.world_id == self.world_id,
                )
                .all()
            )
            return [RevealStore.orm_to_reveal(reveal_orm) for reveal_orm in reveal_orms]

    def get_by_character_id(self, character_id: int) -> List[Reveal]:
        """Get all reveals for a character"""
        with self.Session() as session:
            character = (
                session.query(CharacterORM)
                .filter(CharacterORM.id == character_id)
                .first()
            )

            if character:
                return [
                    RevealStore.orm_to_reveal(reveal) for reveal in character.reveals
                ]
            else:
                return []

    def get_reveal(self, reveal_id: int) -> Reveal | None:
        """Get a specific reveal by ID for the current user and world"""
        with self.Session() as session:
            reveal_orm = (
                session.query(RevealORM)
                .filter(
                    RevealORM.id == reveal_id,
                    RevealORM.user_id == self.user_id,
                    RevealORM.world_id == self.world_id,
                )
                .first()
            )
            if reveal_orm:
                return RevealStore.orm_to_reveal(reveal_orm)
            return None

    def get_by_id(self, reveal_id: int) -> Reveal | None:
        """Get a specific reveal by ID (alias for get_reveal)"""
        return self.get_reveal(reveal_id)

    def create_reveal(self, reveal_data: RevealCreate) -> Reveal:
        """Create a new reveal"""
        with self.Session() as session:
            # Create the reveal without character_ids - much cleaner!
            reveal_dict = reveal_data.model_dump(exclude={"character_ids"})
            reveal_orm = RevealORM(
                **reveal_dict, user_id=self.user_id, world_id=self.world_id
            )

            # Automatic association handling
            if reveal_data.character_ids:
                characters = (
                    session.query(CharacterORM)
                    .filter(CharacterORM.id.in_(reveal_data.character_ids))
                    .all()
                )
                reveal_orm.characters = characters

            session.add(reveal_orm)
            session.commit()
            session.refresh(reveal_orm)
            return RevealStore.orm_to_reveal(reveal_orm)

    def update_reveal(
        self, reveal_id: int, reveal_update: RevealUpdate
    ) -> Reveal | None:
        """Update an existing reveal"""
        with self.Session() as session:
            reveal_orm = (
                session.query(RevealORM)
                .filter(
                    RevealORM.id == reveal_id,
                    RevealORM.user_id == self.user_id,
                    RevealORM.world_id == self.world_id,
                )
                .first()
            )

            if not reveal_orm:
                return None

            # Update basic fields
            update_data = reveal_update.model_dump(
                exclude={"character_ids"}, exclude_unset=True
            )
            for key, value in update_data.items():
                setattr(reveal_orm, key, value)

            # Update character relationships
            if reveal_update.character_ids is not None:
                characters = (
                    session.query(CharacterORM)
                    .filter(CharacterORM.id.in_(reveal_update.character_ids))
                    .all()
                )
                reveal_orm.characters = characters

            session.commit()
            session.refresh(reveal_orm)
            return RevealStore.orm_to_reveal(reveal_orm)

    def delete_reveal(self, reveal_id: int) -> bool:
        """Delete a reveal"""
        with self.Session() as session:
            reveal_orm = (
                session.query(RevealORM)
                .filter(
                    RevealORM.id == reveal_id,
                    RevealORM.user_id == self.user_id,
                    RevealORM.world_id == self.world_id,
                )
                .first()
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
                session.query(RevealORM)
                .filter(
                    RevealORM.id == reveal_id,
                    RevealORM.user_id == self.user_id,
                    RevealORM.world_id == self.world_id,
                )
                .first()
                is not None
            )

    @staticmethod
    def orm_to_reveal(reveal_orm: RevealORM) -> Reveal:
        """Convert RevealORM to Reveal model"""
        return Reveal(
            id=reveal_orm.id,
            user_id=reveal_orm.user_id,
            world_id=reveal_orm.world_id,
            title=reveal_orm.title,
            character_ids=[char.id for char in reveal_orm.characters],
            level_1_content=reveal_orm.level_1_content,
            level_2_content=reveal_orm.level_2_content,
            level_3_content=reveal_orm.level_3_content,
            standard_threshold=reveal_orm.standard_threshold,
            privileged_threshold=reveal_orm.privileged_threshold,
            exclusive_threshold=reveal_orm.exclusive_threshold,
        )
