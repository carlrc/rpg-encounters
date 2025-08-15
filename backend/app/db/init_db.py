from app.db.connection import DB_ENGINE
from app.db.models.character import CharacterORM
from app.db.models.influence import InfluenceORM
from app.db.models.memory import MemoryORM
from app.db.models.memory_character_association import memory_character_association
from app.db.models.player import PlayerORM
from app.db.models.reveal import RevealORM
from app.db.models.reveal_character_association import reveal_character_association


def create_tables():
    """Create all database tables"""
    PlayerORM.metadata.create_all(bind=DB_ENGINE)
    CharacterORM.metadata.create_all(bind=DB_ENGINE)
    MemoryORM.metadata.create_all(bind=DB_ENGINE)
    RevealORM.metadata.create_all(bind=DB_ENGINE)
    InfluenceORM.metadata.create_all(bind=DB_ENGINE)
    memory_character_association.metadata.create_all(bind=DB_ENGINE)
    reveal_character_association.metadata.create_all(bind=DB_ENGINE)


def drop_tables():
    """Drop all database tables"""
    InfluenceORM.metadata.drop_all(bind=DB_ENGINE)
    PlayerORM.metadata.drop_all(bind=DB_ENGINE)
    CharacterORM.metadata.drop_all(bind=DB_ENGINE)
    MemoryORM.metadata.drop_all(bind=DB_ENGINE)
    RevealORM.metadata.drop_all(bind=DB_ENGINE)
    memory_character_association.metadata.drop_all(bind=DB_ENGINE)
    reveal_character_association.metadata.drop_all(bind=DB_ENGINE)


if __name__ == "__main__":
    create_tables()
