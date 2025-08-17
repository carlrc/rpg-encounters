import logging
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from app.db.connection import DB_ENGINE
from app.db.models.player import PlayerORM
from app.db.models.character import CharacterORM
from app.db.models.encounter import EncounterORM
from app.db.models.memory import MemoryORM
from app.db.models.reveal import RevealORM
from app.db.models.connection import ConnectionORM
# Needs to be imported for sqlalchemy
from app.db.models.influence import InfluenceORM  # noqa: F401
from app.db.init_db import create_tables
from tests.fixtures.players import players_db
from tests.fixtures.characters import characters_db
from tests.fixtures.encounters import encounters_db
from tests.fixtures.memories import memories_db
from tests.fixtures.reveals import reveal_db
from tests.fixtures.connections import connections_db

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def migrate_player_data():
    """Migrate player data from fixtures to database"""
    Session = sessionmaker(bind=DB_ENGINE)
    
    try:
        with Session() as session:
            # Check if data already exists
            existing_count = session.query(PlayerORM).count()
            if existing_count > 0:
                logger.info(f"Database already contains {existing_count} players. Skipping migration.")
                return
            
            # Migrate fixture data
            for _, player in players_db.items():
                player_data = player.model_dump()
                # Remove the id since it will be auto-generated
                player_data.pop('id', None)
                
                player_orm = PlayerORM(**player_data)
                session.add(player_orm)
            
            session.commit()
            logger.info(f"Successfully migrated {len(players_db)} players to database!")
    except SQLAlchemyError as e:
        logger.error(f"Error migrating player data: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error migrating player data: {e}")
        raise


def migrate_character_data():
    """Migrate character data from fixtures to database"""
    Session = sessionmaker(bind=DB_ENGINE)
    
    try:
        with Session() as session:
            # Check if data already exists
            existing_count = session.query(CharacterORM).count()
            if existing_count > 0:
                logger.info(f"Database already contains {existing_count} characters. Skipping migration.")
                return
            
            # Migrate fixture data
            for _, character in characters_db.items():
                character_data = character.model_dump()
                # Remove the id since it will be auto-generated
                character_data.pop('id', None)
                
                character_orm = CharacterORM(**character_data)
                session.add(character_orm)
            
            session.commit()
            logger.info(f"Successfully migrated {len(characters_db)} characters to database!")
    except SQLAlchemyError as e:
        logger.error(f"Error migrating character data: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error migrating character data: {e}")
        raise


def migrate_encounter_data():
    """Migrate encounter data from fixtures to database"""
    Session = sessionmaker(bind=DB_ENGINE)
    
    try:
        with Session() as session:
            # Check if data already exists
            existing_count = session.query(EncounterORM).count()
            if existing_count > 0:
                logger.info(f"Database already contains {existing_count} encounters. Skipping migration.")
                return
            
            # Migrate fixture data
            for _, encounter in encounters_db.items():
                encounter_data = encounter.model_dump()
                # Remove the id and character_ids since they will be handled separately
                encounter_data.pop('id', None)
                character_ids = encounter_data.pop('character_ids', [])
                
                encounter_orm = EncounterORM(**encounter_data)
                session.add(encounter_orm)
                session.flush()  # Get the ID for the encounter
                
                # Handle many-to-many relationship with characters
                if character_ids:
                    characters = session.query(CharacterORM).filter(CharacterORM.id.in_(character_ids)).all()
                    if len(characters) != len(character_ids):
                        missing_ids = set(character_ids) - {c.id for c in characters}
                        logger.warning(f"Could not find characters with IDs: {missing_ids}")
                    encounter_orm.characters.extend(characters)
            
            session.commit()
            logger.info(f"Successfully migrated {len(encounters_db)} encounters to database!")
    except SQLAlchemyError as e:
        logger.error(f"Error migrating encounter data: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error migrating encounter data: {e}")
        raise


def migrate_memory_data():
    """Migrate memory data from fixtures to database"""
    Session = sessionmaker(bind=DB_ENGINE)
    
    try:
        with Session() as session:
            # Check if data already exists
            existing_count = session.query(MemoryORM).count()
            if existing_count > 0:
                logger.info(f"Database already contains {existing_count} memories. Skipping migration.")
                return
            
            # Migrate fixture data
            for _, memory in memories_db.items():
                memory_data = memory.model_dump()
                # Remove the id and character_ids since they will be handled separately
                memory_data.pop('id', None)
                character_ids = memory_data.pop('character_ids', [])
                
                memory_orm = MemoryORM(**memory_data)
                session.add(memory_orm)
                session.flush()  # Get the ID for the memory
                
                # Handle many-to-many relationship with characters
                if character_ids:
                    characters = session.query(CharacterORM).filter(CharacterORM.id.in_(character_ids)).all()
                    if len(characters) != len(character_ids):
                        missing_ids = set(character_ids) - {c.id for c in characters}
                        logger.warning(f"Could not find characters with IDs: {missing_ids}")
                    memory_orm.characters.extend(characters)
            
            session.commit()
            logger.info(f"Successfully migrated {len(memories_db)} memories to database!")
    except SQLAlchemyError as e:
        logger.error(f"Error migrating memory data: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error migrating memory data: {e}")
        raise


def migrate_reveal_data():
    """Migrate reveal data from fixtures to database"""
    Session = sessionmaker(bind=DB_ENGINE)
    
    try:
        with Session() as session:
            # Check if data already exists
            existing_count = session.query(RevealORM).count()
            if existing_count > 0:
                logger.info(f"Database already contains {existing_count} reveals. Skipping migration.")
                return
            
            # Migrate fixture data
            for _, reveal in reveal_db.items():
                reveal_data = reveal.model_dump()
                # Remove the id and character_ids since they will be handled separately
                reveal_data.pop('id', None)
                character_ids = reveal_data.pop('character_ids', [])
                
                reveal_orm = RevealORM(**reveal_data)
                session.add(reveal_orm)
                session.flush()  # Get the ID for the reveal
                
                # Handle many-to-many relationship with characters
                if character_ids:
                    characters = session.query(CharacterORM).filter(CharacterORM.id.in_(character_ids)).all()
                    if len(characters) != len(character_ids):
                        missing_ids = set(character_ids) - {c.id for c in characters}
                        logger.warning(f"Could not find characters with IDs: {missing_ids}")
                    reveal_orm.characters.extend(characters)
            
            session.commit()
            logger.info(f"Successfully migrated {len(reveal_db)} reveals to database!")
    except SQLAlchemyError as e:
        logger.error(f"Error migrating reveal data: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error migrating reveal data: {e}")
        raise


def migrate_connection_data():
    """Migrate connection data from fixtures to database"""
    Session = sessionmaker(bind=DB_ENGINE)
    
    try:
        with Session() as session:
            # Check if data already exists
            existing_count = session.query(ConnectionORM).count()
            if existing_count > 0:
                logger.info(f"Database already contains {existing_count} connections. Skipping migration.")
                return
            
            # Migrate fixture data
            for _, connection in connections_db.items():
                connection_data = connection.model_dump()
                # Remove the id since it will be auto-generated
                connection_data.pop('id', None)
                
                # Verify that the referenced encounters exist
                source_encounter = session.query(EncounterORM).filter(
                    EncounterORM.id == connection_data['source_encounter_id']
                ).first()
                target_encounter = session.query(EncounterORM).filter(
                    EncounterORM.id == connection_data['target_encounter_id']
                ).first()
                
                if not source_encounter:
                    logger.warning(f"Source encounter {connection_data['source_encounter_id']} not found")
                    continue
                if not target_encounter:
                    logger.warning(f"Target encounter {connection_data['target_encounter_id']} not found")
                    continue
                
                connection_orm = ConnectionORM(**connection_data)
                session.add(connection_orm)
            
            session.commit()
            logger.info(f"Successfully migrated {len(connections_db)} connections to database!")
    except SQLAlchemyError as e:
        logger.error(f"Error migrating connection data: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error migrating connection data: {e}")
        raise


def migrate_all_data():
    """Migrate all fixture data to database in the correct order"""
    logger.info("Starting migration of all fixture data...")
    
    try:
        # Migrate in dependency order
        migrate_player_data()
        migrate_character_data()
        migrate_encounter_data()
        migrate_memory_data()
        migrate_reveal_data()
        migrate_connection_data()
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        raise


if __name__ == "__main__":
    create_tables()
    migrate_all_data()