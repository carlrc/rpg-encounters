import sys
import asyncio
import logging
from dotenv import load_dotenv

from app.utils import get_or_throw
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from app.db.models.player import PlayerORM
from app.db.models.character import CharacterORM
from app.db.models.encounter import EncounterORM
from app.db.models.memory import MemoryORM
from app.db.models.reveal import RevealORM
from app.db.models.connection import ConnectionORM
from app.db.models.user import UserORM
from app.db.models.world import WorldORM
from app.db.models.account import AccountORM
# Needs to be imported for sqlalchemy
from app.db.models.influence import InfluenceORM  # noqa: F401
from app.db.init_db import create_tables, drop_tables
from app.agents.communication_style_agent import CommunicationStyleAgent, COMMUNICATION_STYLE_PROFILES
from app.agents.personality_agent import PersonalityAgent
from app.agents.prompts.import_prompts import render_prompt
from app.db.limits import CHARACTER_COMMUNICATION_LIMIT
from app.models.character import CommunicationStyle
from app.telemetry import setup_telemetry
from tests.fixtures.players import players_db
from tests.fixtures.characters import characters_db
from tests.fixtures.encounters import encounters_db
from tests.fixtures.memories import memories_db
from tests.fixtures.reveals import reveal_db
from tests.fixtures.connections import connections_db
from sqlalchemy.ext.asyncio import create_async_engine

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def get_user_and_world_ids(session):
    """Helper method to get user and world IDs from database"""
    result = await session.execute(select(UserORM))
    user = result.scalars().first()
    result = await session.execute(select(WorldORM))
    world = result.scalars().first()
    
    if not user:
        logger.error("No user found in database. Cannot create entities.")
        raise Exception("No user found for entity creation")
    
    if not world:
        logger.error("No world found in database. Cannot create entities.")
        raise Exception("No world found for entity creation")
    
    logger.info(f"Using user_id={user.id} and world_id={world.id} for entity creation")
    return user.id, world.id

async def seed_user_data(engine: AsyncEngine):
    """Create user for testing"""
    AsyncSession = async_sessionmaker(bind=engine, expire_on_commit=False)
    
    try:
        async with AsyncSession() as session:
            # Check if any user already exists
            result = await session.execute(select(UserORM))
            existing_user = result.scalars().first()
            if existing_user:
                logger.info("User already exists. Skipping user creation.")
                return
            
            # Create user (let autoincrement handle the ID)
            user = UserORM()
            session.add(user)
            await session.flush()
            await session.commit()
            logger.info(f"Created user with ID: {user.id}")
    except SQLAlchemyError as e:
        logger.error(f"Error creating user data: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error creating user data: {e}")
        raise

async def seed_world_data(engine: AsyncEngine):
    """Create world for testing"""
    AsyncSession = async_sessionmaker(bind=engine, expire_on_commit=False)
    
    try:
        async with AsyncSession() as session:
            # Check if any world already exists
            result = await session.execute(select(WorldORM))
            existing_world = result.scalars().first()
            if existing_world:
                logger.info("World already exists. Skipping world creation.")
                return
            
            # Get the first user to associate with the world
            result = await session.execute(select(UserORM))
            user = result.scalars().first()
            if not user:
                logger.error("No user found. Cannot create world.")
                raise Exception("No user found for world creation")
            
            # Create world (let autoincrement handle the ID)
            world = WorldORM(user_id=user.id)
            session.add(world)
            await session.flush()
            await session.commit()
            logger.info(f"Created world with ID: {world.id} for user ID: {user.id}")
    except SQLAlchemyError as e:
        logger.error(f"Error creating world data: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error creating world data: {e}")
        raise

async def seed_account_data(engine: AsyncEngine):
    """Create account for testing user"""
    AsyncSession = async_sessionmaker(bind=engine, expire_on_commit=False)
    
    try:
        async with AsyncSession() as session:
            # Check if account already exists
            result = await session.execute(select(AccountORM))
            existing_account = result.scalars().first()
            if existing_account:
                logger.info("Account already exists. Skipping account creation.")
                return
            
            # Get the user to associate with the account
            result = await session.execute(select(UserORM))
            user = result.scalars().first()
            if not user:
                logger.error("No user found. Cannot create account.")
                raise Exception("No user found for account creation")
            
            # Create account with test email
            account = AccountORM(
                user_id=user.id,
                email="test@example.com",
                elevenlabs_token=None
            )
            session.add(account)
            await session.flush()
            await session.commit()
            logger.info(f"Created account with email: test@example.com for user ID: {user.id}")
    except SQLAlchemyError as e:
        logger.error(f"Error creating account data: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error creating account data: {e}")
        raise

async def seed_player_data(engine: AsyncEngine):
    """Seed player data from fixtures to database"""
    AsyncSession = async_sessionmaker(bind=engine, expire_on_commit=False)
    
    try:
        async with AsyncSession() as session:
            result = await session.execute(select(PlayerORM))
            existing_count = len(result.scalars().all())
            if existing_count > 0:
                logger.info(f"Database already contains {existing_count} players. Skipping migration.")
                return
            
            # Get the actual user and world IDs from the database
            user_id, world_id = await get_user_and_world_ids(session)
            
            # Migrate fixture data with actual user_id and world_id
            for player in players_db:
                player_data = player.model_dump()
                logger.info(f"Creating player '{player_data['name']}' with user_id={user_id}, world_id={world_id}")
                
                player_orm = PlayerORM(**player_data, user_id=user_id, world_id=world_id)
                session.add(player_orm)
            
            await session.commit()
            logger.info(f"Successfully seeded {len(players_db)} players to database!")
    except SQLAlchemyError as e:
        logger.error(f"Error seeding player data: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error seeding player data: {e}")
        raise

async def seed_character_data(engine: AsyncEngine):
    """Seed character data from fixtures to database"""
    AsyncSession = async_sessionmaker(bind=engine, expire_on_commit=False)
    
    try:
        async with AsyncSession() as session:
            # Check if data already exists
            result = await session.execute(select(CharacterORM))
            existing_count = len(result.scalars().all())
            if existing_count > 0:
                logger.info(f"Database already contains {existing_count} characters. Skipping migration.")
                return
            
            # Get the actual user and world IDs from the database
            user_id, world_id = await get_user_and_world_ids(session)
            
            # Seed fixture data
            for character in characters_db:
                if character.communication_style_type != CommunicationStyle.CUSTOM.value:
                    # Create communication style agent for each character with proper context
                    system_prompt = render_prompt(
                        "communication_style_agent",
                        {
                            "character": character,
                            "style_profile": COMMUNICATION_STYLE_PROFILES[character.communication_style_type],
                            "max_response_length": CHARACTER_COMMUNICATION_LIMIT,
                        }
                    )
                    communication_style_agent = CommunicationStyleAgent(system_prompt=system_prompt)
                    communication_style = await communication_style_agent.generate(character=character)
                    character.communication_style = communication_style.style_summary
                    character.communication_style_examples = communication_style.examples
                    
                character.personality = await PersonalityAgent().generate(character=character)
                character_data = character.model_dump()
                logger.info(f"Creating character '{character_data['name']}' with user_id={user_id}, world_id={world_id}")
                
                character_orm = CharacterORM(**character_data, user_id=user_id, world_id=world_id)
                session.add(character_orm)
            
            await session.commit()
            logger.info(f"Successfully seeded {len(characters_db)} characters to database!")
    except SQLAlchemyError as e:
        logger.error(f"Error seeding character data: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error seeding character data: {e}")
        raise

async def seed_encounter_data(engine: AsyncEngine):
    """Seed encounter data from fixtures to database"""
    AsyncSession = async_sessionmaker(bind=engine, expire_on_commit=False)
    
    try:
        async with AsyncSession() as session:
            # Check if data already exists
            result = await session.execute(select(EncounterORM))
            existing_count = len(result.scalars().all())
            if existing_count > 0:
                logger.info(f"Database already contains {existing_count} encounters. Skipping migration.")
                return
            
            # Get all characters in order (they were created in array order)
            result = await session.execute(select(CharacterORM).order_by(CharacterORM.id))
            characters = result.scalars().all()

            # Get the actual user and world IDs from the database
            user_id, world_id = await get_user_and_world_ids(session)
            
            # Seed fixture data
            for encounter in encounters_db:
                encounter_data = encounter.model_dump()
                # Extract character_ids (these are array indices)
                character_indices = encounter_data.pop('character_ids', [])
                
                encounter_orm = EncounterORM(**encounter_data, user_id=user_id, world_id=world_id)
                session.add(encounter_orm)
                await session.flush()
                
                # Map array indices to actual characters
                if character_indices:
                    selected_characters = [characters[i] for i in character_indices if i < len(characters)]
                    await session.run_sync(lambda sync_session: setattr(encounter_orm, 'characters', selected_characters))
                else:
                    await session.run_sync(lambda sync_session: setattr(encounter_orm, 'characters', []))
            
            await session.commit()
            logger.info(f"Successfully seeded {len(encounters_db)} encounters to database!")
    except SQLAlchemyError as e:
        logger.error(f"Error seeding encounter data: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error seeding encounter data: {e}")
        raise

async def seed_memory_data(engine: AsyncEngine):
    """Seed memory data from fixtures to database"""
    AsyncSession = async_sessionmaker(bind=engine, expire_on_commit=False)
    
    try:
        async with AsyncSession() as session:
            # Check if data already exists
            result = await session.execute(select(MemoryORM))
            existing_count = len(result.scalars().all())
            if existing_count > 0:
                logger.info(f"Database already contains {existing_count} memories. Skipping migration.")
                return
            
            # Get all characters in order
            result = await session.execute(select(CharacterORM).order_by(CharacterORM.id))
            characters = result.scalars().all()

            # Get the actual user and world IDs from the database
            user_id, world_id = await get_user_and_world_ids(session)
            
            # Seed fixture data
            for memory in memories_db:
                memory_data = memory.model_dump()
                # Extract character_ids (these are array indices)
                character_indices = memory_data.pop('character_ids', [])
                
                memory_orm = MemoryORM(**memory_data, user_id=user_id, world_id=world_id)
                session.add(memory_orm)
                await session.flush()  # Get the ID for the memory
                
                # Map array indices to actual characters
                if character_indices:
                    selected_characters = [characters[i] for i in character_indices if i < len(characters)]
                    await session.run_sync(lambda sync_session: setattr(memory_orm, 'characters', selected_characters))
                else:
                    await session.run_sync(lambda sync_session: setattr(memory_orm, 'characters', []))
            
            await session.commit()
            logger.info(f"Successfully seeded {len(memories_db)} memories to database!")
    except SQLAlchemyError as e:
        logger.error(f"Error seeding memory data: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error seeding memory data: {e}")
        raise

async def seed_reveal_data(engine: AsyncEngine):
    """Seed reveal data from fixtures to database"""
    AsyncSession = async_sessionmaker(bind=engine, expire_on_commit=False)
    
    try:
        async with AsyncSession() as session:
            # Check if data already exists
            result = await session.execute(select(RevealORM))
            existing_count = len(result.scalars().all())
            if existing_count > 0:
                logger.info(f"Database already contains {existing_count} reveals. Skipping migration.")
                return
            
            # Get all characters in order
            result = await session.execute(select(CharacterORM).order_by(CharacterORM.id))
            characters = result.scalars().all()

            # Get the actual user and world IDs from the database
            user_id, world_id = await get_user_and_world_ids(session)
            
            # Seed fixture data
            for reveal in reveal_db:
                reveal_data = reveal.model_dump()
                # Extract character_ids (these are array indices)
                character_indices = reveal_data.pop('character_ids', [])
                
                reveal_orm = RevealORM(**reveal_data, user_id=user_id, world_id=world_id)
                session.add(reveal_orm)
                await session.flush()  # Get the ID for the reveal
                
                # Map array indices to actual characters
                if character_indices:
                    selected_characters = [characters[i] for i in character_indices if i < len(characters)]
                    await session.run_sync(lambda sync_session: setattr(reveal_orm, 'characters', selected_characters))
                else:
                    await session.run_sync(lambda sync_session: setattr(reveal_orm, 'characters', []))
            
            await session.commit()
            logger.info(f"Successfully seeded {len(reveal_db)} reveals to database!")
    except SQLAlchemyError as e:
        logger.error(f"Error seeding reveal data: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error seeding reveal data: {e}")
        raise

async def seed_connection_data(engine: AsyncEngine):
    """Seed connection data from fixtures to database"""
    AsyncSession = async_sessionmaker(bind=engine, expire_on_commit=False)
    
    try:
        async with AsyncSession() as session:
            # Check if data already exists
            result = await session.execute(select(ConnectionORM))
            existing_count = len(result.scalars().all())
            if existing_count > 0:
                logger.info(f"Database already contains {existing_count} connections. Skipping migration.")
                return
            
            # Get all encounters in order
            result = await session.execute(select(EncounterORM).order_by(EncounterORM.id))
            encounters = result.scalars().all()

            # Get the actual user and world IDs from the database
            user_id, world_id = await get_user_and_world_ids(session)
            
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
            
            await session.commit()
            logger.info(f"Successfully seeded {len(connections_db)} connections to database!")
    except SQLAlchemyError as e:
        logger.error(f"Error seeding connection data: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error seeding connection data: {e}")
        raise

async def seed_all_data(engine: AsyncEngine):
    """Seed all fixture data to database in the correct order"""
    try:
        # Seed required user and world data first
        await seed_user_data(engine=engine)
        await seed_world_data(engine=engine)
        await seed_account_data(engine=engine)
        
        # Seed in dependency order
        await seed_player_data(engine=engine)
        await seed_character_data(engine=engine)
        await seed_encounter_data(engine=engine)
        await seed_memory_data(engine=engine)
        await seed_reveal_data(engine=engine)
        await seed_connection_data(engine=engine)

        logger.info(f"✅ All data seeded!")
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        await drop_tables(engine=engine)
        raise

async def main():
    # Check for --prod flag to use live database
    use_dev = "--dev" not in sys.argv
    
    if not use_dev:
        print("🔴 Seeding to DEV database")
        url = get_or_throw("DATABASE_URL")
    else:
        print("🟢 Seeding to TEST database (default)")
        url = get_or_throw("TEST_DATABASE_URL")

    engine = create_async_engine(url)
    await drop_tables(engine=engine)
    await create_tables(engine=engine)
    setup_telemetry()
    await seed_all_data(engine=engine)

if __name__ == "__main__":
    asyncio.run(main())