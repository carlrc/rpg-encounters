import os
import sys
import logging
from dotenv import load_dotenv
from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from app.db.connection import get_db_engine
from app.db.models.player import PlayerORM
from app.db.models.character import CharacterORM
from app.db.models.encounter import EncounterORM
from app.db.models.memory import MemoryORM
from app.db.models.reveal import RevealORM
from app.db.models.connection import ConnectionORM
from app.db.models.user import UserORM
from app.db.models.world import WorldORM
# Needs to be imported for sqlalchemy
from app.db.models.influence import InfluenceORM  # noqa: F401
from app.db.init_db import create_tables, drop_tables
from tests.fixtures.players import players_db
from tests.fixtures.characters import characters_db
from tests.fixtures.encounters import encounters_db
from tests.fixtures.memories import memories_db
from tests.fixtures.reveals import reveal_db
from tests.fixtures.connections import connections_db

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_user_and_world_ids(session):
    """Helper method to get user and world IDs from database"""
    user = session.query(UserORM).first()
    world = session.query(WorldORM).first()
    
    if not user:
        logger.error("No user found in database. Cannot create entities.")
        raise Exception("No user found for entity creation")
    
    if not world:
        logger.error("No world found in database. Cannot create entities.")
        raise Exception("No world found for entity creation")
    
    logger.info(f"Using user_id={user.id} and world_id={world.id} for entity creation")
    return user.id, world.id

def seed_user_data(engine: Engine):
    """Create user for testing"""
    Session = sessionmaker(bind=engine)
    
    try:
        with Session() as session:
            # Check if any user already exists
            existing_user = session.query(UserORM).first()
            if existing_user:
                logger.info("User already exists. Skipping user creation.")
                return
            
            # Create user (let autoincrement handle the ID)
            user = UserORM()
            session.add(user)
            session.commit()
            logger.info(f"Created user with ID: {user.id}")
    except SQLAlchemyError as e:
        logger.error(f"Error creating user data: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error creating user data: {e}")
        raise

def seed_world_data(engine: Engine):
    """Create world for testing"""
    Session = sessionmaker(bind=engine)
    
    try:
        with Session() as session:
            # Check if any world already exists
            existing_world = session.query(WorldORM).first()
            if existing_world:
                logger.info("World already exists. Skipping world creation.")
                return
            
            # Get the first user to associate with the world
            user = session.query(UserORM).first()
            if not user:
                logger.error("No user found. Cannot create world.")
                raise Exception("No user found for world creation")
            
            # Create world (let autoincrement handle the ID)
            world = WorldORM(user_id=user.id)
            session.add(world)
            session.commit()
            logger.info(f"Created world with ID: {world.id} for user ID: {user.id}")
    except SQLAlchemyError as e:
        logger.error(f"Error creating world data: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error creating world data: {e}")
        raise


def seed_player_data(engine: Engine):
    """Seed player data from fixtures to database"""
    Session = sessionmaker(bind=engine)
    
    try:
        with Session() as session:
            existing_count = session.query(PlayerORM).count()
            if existing_count > 0:
                logger.info(f"Database already contains {existing_count} players. Skipping migration.")
                return
            
            # Get the actual user and world IDs from the database
            user_id, world_id = get_user_and_world_ids(session)
            
            # Migrate fixture data with actual user_id and world_id
            for player in players_db:
                player_data = player.model_dump()
                logger.info(f"Creating player '{player_data['name']}' with user_id={user_id}, world_id={world_id}")
                
                player_orm = PlayerORM(**player_data, user_id=user_id, world_id=world_id)
                session.add(player_orm)
            
            session.commit()
            logger.info(f"Successfully seeded {len(players_db)} players to database!")
    except SQLAlchemyError as e:
        logger.error(f"Error seeding player data: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error seeding player data: {e}")
        raise


def seed_character_data(engine: Engine):
    """Seed character data from fixtures to database"""
    Session = sessionmaker(bind=engine)
    
    try:
        with Session() as session:
            # Check if data already exists
            existing_count = session.query(CharacterORM).count()
            if existing_count > 0:
                logger.info(f"Database already contains {existing_count} characters. Skipping migration.")
                return
            
            # Get the actual user and world IDs from the database
            user_id, world_id = get_user_and_world_ids(session)
            
            # Seed fixture data with actual user_id and world_id
            for character in characters_db:
                character_data = character.model_dump()
                logger.info(f"Creating character '{character_data['name']}' with user_id={user_id}, world_id={world_id}")
                
                character_orm = CharacterORM(**character_data, user_id=user_id, world_id=world_id)
                session.add(character_orm)
            
            session.commit()
            logger.info(f"Successfully seeded {len(characters_db)} characters to database!")
    except SQLAlchemyError as e:
        logger.error(f"Error seeding character data: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error seeding character data: {e}")
        raise


def seed_encounter_data(engine: Engine):
    """Seed encounter data from fixtures to database"""
    Session = sessionmaker(bind=engine)
    
    try:
        with Session() as session:
            # Check if data already exists
            existing_count = session.query(EncounterORM).count()
            if existing_count > 0:
                logger.info(f"Database already contains {existing_count} encounters. Skipping migration.")
                return
            
            # Get all characters in order (they were created in array order)
            characters = session.query(CharacterORM).order_by(CharacterORM.id).all()

            # Get the actual user and world IDs from the database
            user_id, world_id = get_user_and_world_ids(session)
            
            # Seed fixture data
            for encounter in encounters_db:
                encounter_data = encounter.model_dump()
                # Extract character_ids (these are array indices)
                character_indices = encounter_data.pop('character_ids', [])
                
                encounter_orm = EncounterORM(**encounter_data, user_id=user_id, world_id=world_id)
                session.add(encounter_orm)
                session.flush()
                
                # Map array indices to actual characters
                if character_indices:
                    selected_characters = [characters[i] for i in character_indices if i < len(characters)]
                    encounter_orm.characters.extend(selected_characters)
            
            session.commit()
            logger.info(f"Successfully seeded {len(encounters_db)} encounters to database!")
    except SQLAlchemyError as e:
        logger.error(f"Error seeding encounter data: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error seeding encounter data: {e}")
        raise


def seed_memory_data(engine: Engine):
    """Seed memory data from fixtures to database"""
    Session = sessionmaker(bind=engine)
    
    try:
        with Session() as session:
            # Check if data already exists
            existing_count = session.query(MemoryORM).count()
            if existing_count > 0:
                logger.info(f"Database already contains {existing_count} memories. Skipping migration.")
                return
            
            # Get all characters in order
            characters = session.query(CharacterORM).order_by(CharacterORM.id).all()

            # Get the actual user and world IDs from the database
            user_id, world_id = get_user_and_world_ids(session)
            
            # Seed fixture data
            for memory in memories_db:
                memory_data = memory.model_dump()
                # Extract character_ids (these are array indices)
                character_indices = memory_data.pop('character_ids', [])
                
                memory_orm = MemoryORM(**memory_data, user_id=user_id, world_id=world_id)
                session.add(memory_orm)
                session.flush()  # Get the ID for the memory
                
                # Map array indices to actual characters
                if character_indices:
                    selected_characters = [characters[i] for i in character_indices if i < len(characters)]
                    memory_orm.characters.extend(selected_characters)
            
            session.commit()
            logger.info(f"Successfully seeded {len(memories_db)} memories to database!")
    except SQLAlchemyError as e:
        logger.error(f"Error seeding memory data: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error seeding memory data: {e}")
        raise


def seed_reveal_data(engine: Engine):
    """Seed reveal data from fixtures to database"""
    Session = sessionmaker(bind=engine)
    
    try:
        with Session() as session:
            # Check if data already exists
            existing_count = session.query(RevealORM).count()
            if existing_count > 0:
                logger.info(f"Database already contains {existing_count} reveals. Skipping migration.")
                return
            
            # Get all characters in order
            characters = session.query(CharacterORM).order_by(CharacterORM.id).all()

            # Get the actual user and world IDs from the database
            user_id, world_id = get_user_and_world_ids(session)
            
            # Seed fixture data
            for reveal in reveal_db:
                reveal_data = reveal.model_dump()
                # Extract character_ids (these are array indices)
                character_indices = reveal_data.pop('character_ids', [])
                
                reveal_orm = RevealORM(**reveal_data, user_id=user_id, world_id=world_id)
                session.add(reveal_orm)
                session.flush()  # Get the ID for the reveal
                
                # Map array indices to actual characters
                if character_indices:
                    selected_characters = [characters[i] for i in character_indices if i < len(characters)]
                    reveal_orm.characters.extend(selected_characters)
            
            session.commit()
            logger.info(f"Successfully seeded {len(reveal_db)} reveals to database!")
    except SQLAlchemyError as e:
        logger.error(f"Error seeding reveal data: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error seeding reveal data: {e}")
        raise


def seed_connection_data(engine: Engine):
    """Seed connection data from fixtures to database"""
    Session = sessionmaker(bind=engine)
    
    try:
        with Session() as session:
            # Check if data already exists
            existing_count = session.query(ConnectionORM).count()
            if existing_count > 0:
                logger.info(f"Database already contains {existing_count} connections. Skipping migration.")
                return
            
            # Get all encounters in order
            encounters = session.query(EncounterORM).order_by(EncounterORM.id).all()

            # Get the actual user and world IDs from the database
            user_id, world_id = get_user_and_world_ids(session)
            
            # Migrate fixture data (now an array)
            for connection in connections_db:
                connection_data = connection.model_dump()
                
                # Map array indices to actual encounter IDs
                source_idx = connection_data['source_encounter_id']
                target_idx = connection_data['target_encounter_id']
                
                if source_idx < len(encounters) and target_idx < len(encounters):
                    connection_data['source_encounter_id'] = encounters[source_idx].id
                    connection_data['target_encounter_id'] = encounters[target_idx].id
                    
                    connection_orm = ConnectionORM(**connection_data, user_id=user_id, world_id=world_id)
                    session.add(connection_orm)
                else:
                    logger.warning(f"Encounter indices out of range: source={source_idx}, target={target_idx}")
            
            session.commit()
            logger.info(f"Successfully seeded {len(connections_db)} connections to database!")
    except SQLAlchemyError as e:
        logger.error(f"Error seeding connection data: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error seeding connection data: {e}")
        raise


def seed_all_data(engine: Engine):
    """Seed all fixture data to database in the correct order"""
    try:
        # Seed required user and world data first
        seed_user_data(engine=engine)
        seed_world_data(engine=engine)
        
        # Seed in dependency order
        seed_player_data(engine=engine)
        seed_character_data(engine=engine)
        seed_encounter_data(engine=engine)
        seed_memory_data(engine=engine)
        seed_reveal_data(engine=engine)
        seed_connection_data(engine=engine)

        logger.info(f"✅ All data seeded!")
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        drop_tables(engine=engine)
        raise


if __name__ == "__main__":
    # Check for --prod flag to use live database
    use_dev = "--dev" not in sys.argv
    
    if not use_dev:
        print("🔴 Seeding to DEV database")
        url = os.getenv("DATABASE_URL")
    else:
        print("🟢 Seeding to TEST database (default)")
        url = os.getenv("TEST_DATABASE_URL")

    engine = create_engine(url)
    drop_tables(engine=engine)
    create_tables(engine=engine)
    seed_all_data(engine=engine)