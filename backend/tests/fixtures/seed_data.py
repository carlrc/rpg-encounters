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


async def seed_user_data(engine: AsyncEngine, num_users: int = 2) -> list[int]:
    """Create specified number of users for testing and return their IDs"""
    AsyncSession = async_sessionmaker(bind=engine, expire_on_commit=False)

    try:
        async with AsyncSession() as session:
            # Check if any users already exist
            result = await session.execute(select(UserORM))
            existing_users = result.scalars().all()
            if existing_users:
                logger.info(f"Users already exist ({len(existing_users)}). Returning existing IDs.")
                return [user.id for user in existing_users]

            # Create the specified number of users
            user_ids = []
            for i in range(num_users):
                user = UserORM()
                session.add(user)
                await session.flush()
                user_ids.append(user.id)
                logger.info(f"Created user {i+1} with ID: {user.id}")

            await session.commit()
            return user_ids
    except SQLAlchemyError as e:
        logger.error(f"Error creating user data: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error creating user data: {e}")
        raise

async def seed_world_data(engine: AsyncEngine, user_ids: list[int]) -> list[int]:
    """Create worlds for testing and return their IDs"""
    AsyncSession = async_sessionmaker(bind=engine, expire_on_commit=False)

    try:
        async with AsyncSession() as session:
            # Check if any worlds already exist
            result = await session.execute(select(WorldORM))
            existing_worlds = result.scalars().all()
            if existing_worlds:
                logger.info(f"Worlds already exist ({len(existing_worlds)}). Returning existing IDs.")
                return [world.id for world in existing_worlds]

            # Create world for each user
            world_ids = []
            for user_id in user_ids:
                world = WorldORM(user_id=user_id)
                session.add(world)
                await session.flush()
                world_ids.append(world.id)
                logger.info(f"Created world with ID: {world.id} for user ID: {user_id}")

            await session.commit()
            return world_ids
    except SQLAlchemyError as e:
        logger.error(f"Error creating world data: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error creating world data: {e}")
        raise

async def seed_account_data(engine: AsyncEngine, user_ids: list[int]):
    """Create accounts for testing users"""
    AsyncSession = async_sessionmaker(bind=engine, expire_on_commit=False)

    try:
        async with AsyncSession() as session:
            # Check if accounts already exist
            result = await session.execute(select(AccountORM))
            existing_accounts = result.scalars().all()
            if existing_accounts:
                logger.info(f"Accounts already exist ({len(existing_accounts)}). Skipping account creation.")
                return


            for i, user_id in enumerate(user_ids):
                email = f"test{i+1}@example.com"
                account = AccountORM(
                    user_id=user_id,
                    email=email,
                    elevenlabs_token=None
                )
                session.add(account)
                await session.flush()
                logger.info(f"Created account with email: {email} for user ID: {user_id}")

            await session.commit()
    except SQLAlchemyError as e:
        logger.error(f"Error creating account data: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error creating account data: {e}")
        raise

async def seed_player_data(engine: AsyncEngine, user_ids: list[int], world_ids: list[int]):
    """Seed player data from fixtures to database"""
    AsyncSession = async_sessionmaker(bind=engine, expire_on_commit=False)

    try:
        async with AsyncSession() as session:
            result = await session.execute(select(PlayerORM))
            existing_count = len(result.scalars().all())
            if existing_count > 0:
                logger.info(f"Database already contains {existing_count} players. Skipping migration.")
                return

            # Apply same fixture data to each user
            for i, (user_id, world_id) in enumerate(zip(user_ids, world_ids)):
                for player in players_db:
                    player_data = player.model_dump()
                    player_data.pop('id', None)  # Remove ID to let autoincrement handle it
                    logger.info(f"Creating player '{player_data['name']}' for user {i+1} with user_id={user_id}, world_id={world_id}")

                    player_orm = PlayerORM(**player_data, user_id=user_id, world_id=world_id)
                    session.add(player_orm)

            await session.commit()
            logger.info(f"Successfully seeded {len(players_db) * len(user_ids)} players to database! ({len(players_db)} per user)")
    except SQLAlchemyError as e:
        logger.error(f"Error seeding player data: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error seeding player data: {e}")
        raise

async def seed_character_data(engine: AsyncEngine, user_ids: list[int], world_ids: list[int]):
    """Seed character data from fixtures to database"""
    AsyncSession = async_sessionmaker(bind=engine, expire_on_commit=False)

    try:
        async with AsyncSession() as session:
            # Check if data already exists
            result = await session.execute(select(CharacterORM))
            existing_count = len(result.scalars().all())
            if existing_count > 0:
                logger.info(f"Database already contains {existing_count} characters. Skipping seeding...")
                return

            # Prepare all character generation tasks for concurrent execution
            async def generate_character_for_user(character, user_id, world_id, user_index):
                """Generate a single character with AI agents for a specific user"""
                # Create a copy to avoid modifying the original
                character_copy = character.model_copy()

                if character_copy.communication_style_type != CommunicationStyle.CUSTOM.value:
                    # Create communication style agent for each character with proper context
                    system_prompt = render_prompt(
                        "communication_style_agent",
                        {
                            "character": character_copy,
                            "style_profile": COMMUNICATION_STYLE_PROFILES[character_copy.communication_style_type],
                            "max_response_length": CHARACTER_COMMUNICATION_LIMIT,
                        }
                    )
                    communication_style = await CommunicationStyleAgent(system_prompt=system_prompt).generate()
                    character_copy.communication_style = communication_style.style_summary
                    character_copy.communication_style_examples = communication_style.examples

                character_copy.personality = await PersonalityAgent().generate(character=character_copy)
                character_data = character_copy.model_dump()
                character_data.pop('id', None)  # Remove ID to let autoincrement handle it
                logger.info(f"Generated character '{character_data['name']}' for user {user_index+1}")

                return character_data, user_id, world_id

            # Create all generation tasks
            generation_tasks = []
            for i, (user_id, world_id) in enumerate(zip(user_ids, world_ids)):
                for character in characters_db:
                    task = generate_character_for_user(character, user_id, world_id, i)
                    generation_tasks.append(task)

            # Execute all character generation concurrently
            logger.info(f"Starting concurrent generation of {len(generation_tasks)} characters...")
            generated_characters = await asyncio.gather(*generation_tasks)
            logger.info(f"Completed concurrent character generation!")

            # Add all generated characters to the session
            for character_data, user_id, world_id in generated_characters:
                character_orm = CharacterORM(**character_data, user_id=user_id, world_id=world_id)
                session.add(character_orm)

            await session.commit()
            logger.info(f"Successfully seeded {len(characters_db) * len(user_ids)} characters to database! ({len(characters_db)} per user)")
    except SQLAlchemyError as e:
        logger.error(f"Error seeding character data: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error seeding character data: {e}")
        raise

async def seed_encounter_data(engine: AsyncEngine, user_ids: list[int], world_ids: list[int]):
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

            # Apply same fixture data to each user
            for i, (user_id, world_id) in enumerate(zip(user_ids, world_ids)):
                # Get characters for this specific user
                result = await session.execute(
                    select(CharacterORM)
                    .where(CharacterORM.user_id == user_id)
                    .order_by(CharacterORM.id)
                )
                user_characters = result.scalars().all()

                for encounter in encounters_db:
                    encounter_data = encounter.model_dump()
                    encounter_data.pop('id', None)  # Remove ID to let autoincrement handle it
                    # Extract character_ids (these are array indices)
                    character_indices = encounter_data.pop('character_ids', [])

                    encounter_orm = EncounterORM(**encounter_data, user_id=user_id, world_id=world_id)
                    session.add(encounter_orm)
                    await session.flush()

                    # Map array indices to actual characters from this user's characters
                    if character_indices:
                        selected_characters = [user_characters[idx] for idx in character_indices if idx < len(user_characters)]
                        await session.run_sync(lambda sync_session: setattr(encounter_orm, 'characters', selected_characters))
                    else:
                        await session.run_sync(lambda sync_session: setattr(encounter_orm, 'characters', []))

                    logger.info(f"Creating encounter '{encounter_data['name']}' for user {i+1} with user_id={user_id}, world_id={world_id}")

            await session.commit()
            logger.info(f"Successfully seeded {len(encounters_db) * len(user_ids)} encounters to database! ({len(encounters_db)} per user)")
    except SQLAlchemyError as e:
        logger.error(f"Error seeding encounter data: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error seeding encounter data: {e}")
        raise

async def seed_memory_data(engine: AsyncEngine, user_ids: list[int], world_ids: list[int]):
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

            # Apply same fixture data to each user
            for i, (user_id, world_id) in enumerate(zip(user_ids, world_ids)):
                # Get characters for this specific user
                result = await session.execute(
                    select(CharacterORM)
                    .where(CharacterORM.user_id == user_id)
                    .order_by(CharacterORM.id)
                )
                user_characters = result.scalars().all()

                for memory in memories_db:
                    memory_data = memory.model_dump()
                    memory_data.pop('id', None)  # Remove ID to let autoincrement handle it
                    # Extract character_ids (these are array indices)
                    character_indices = memory_data.pop('character_ids', [])

                    memory_orm = MemoryORM(**memory_data, user_id=user_id, world_id=world_id)
                    session.add(memory_orm)
                    await session.flush()  # Get the ID for the memory

                    # Map array indices to actual characters from this user's characters
                    if character_indices:
                        selected_characters = [user_characters[idx] for idx in character_indices if idx < len(user_characters)]
                        await session.run_sync(lambda sync_session: setattr(memory_orm, 'characters', selected_characters))
                    else:
                        await session.run_sync(lambda sync_session: setattr(memory_orm, 'characters', []))

                    logger.info(f"Creating memory '{memory_data['title']}' for user {i+1} with user_id={user_id}, world_id={world_id}")

            await session.commit()
            logger.info(f"Successfully seeded {len(memories_db) * len(user_ids)} memories to database! ({len(memories_db)} per user)")
    except SQLAlchemyError as e:
        logger.error(f"Error seeding memory data: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error seeding memory data: {e}")
        raise

async def seed_reveal_data(engine: AsyncEngine, user_ids: list[int], world_ids: list[int]):
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

            # Apply same fixture data to each user
            for i, (user_id, world_id) in enumerate(zip(user_ids, world_ids)):
                # Get characters for this specific user
                result = await session.execute(
                    select(CharacterORM)
                    .where(CharacterORM.user_id == user_id)
                    .order_by(CharacterORM.id)
                )
                user_characters = result.scalars().all()

                for reveal in reveal_db:
                    reveal_data = reveal.model_dump()
                    reveal_data.pop('id', None)  # Remove ID to let autoincrement handle it
                    # Extract character_ids (these are array indices)
                    character_indices = reveal_data.pop('character_ids', [])

                    reveal_orm = RevealORM(**reveal_data, user_id=user_id, world_id=world_id)
                    session.add(reveal_orm)
                    await session.flush()  # Get the ID for the reveal

                    # Map array indices to actual characters from this user's characters
                    if character_indices:
                        selected_characters = [user_characters[idx] for idx in character_indices if idx < len(user_characters)]
                        await session.run_sync(lambda sync_session: setattr(reveal_orm, 'characters', selected_characters))
                    else:
                        await session.run_sync(lambda sync_session: setattr(reveal_orm, 'characters', []))

                    logger.info(f"Creating reveal '{reveal_data['title']}' for user {i+1} with user_id={user_id}, world_id={world_id}")

            await session.commit()
            logger.info(f"Successfully seeded {len(reveal_db) * len(user_ids)} reveals to database! ({len(reveal_db)} per user)")
    except SQLAlchemyError as e:
        logger.error(f"Error seeding reveal data: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error seeding reveal data: {e}")
        raise

async def seed_connection_data(engine: AsyncEngine, user_ids: list[int], world_ids: list[int]):
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

            # Apply same fixture data to each user
            for i, (user_id, world_id) in enumerate(zip(user_ids, world_ids)):
                # Get encounters for this specific user
                result = await session.execute(
                    select(EncounterORM)
                    .where(EncounterORM.user_id == user_id)
                    .order_by(EncounterORM.id)
                )
                user_encounters = result.scalars().all()

                for connection in connections_db:
                    connection_data = connection.model_dump()
                    connection_data.pop('id', None)  # Remove ID to let autoincrement handle it

                    # Map array indices to actual encounter IDs from this user's encounters
                    source_idx = connection_data['source_encounter_id']
                    target_idx = connection_data['target_encounter_id']

                    if source_idx < len(user_encounters) and target_idx < len(user_encounters):
                        connection_data['source_encounter_id'] = user_encounters[source_idx].id
                        connection_data['target_encounter_id'] = user_encounters[target_idx].id

                        connection_orm = ConnectionORM(**connection_data, user_id=user_id, world_id=world_id)
                        session.add(connection_orm)
                        logger.info(f"Creating connection for user {i+1} with user_id={user_id}, world_id={world_id}")
                    else:
                        logger.warning(f"Encounter indices out of range for user {i+1}: source={source_idx}, target={target_idx}")

            await session.commit()
            logger.info(f"Successfully seeded {len(connections_db) * len(user_ids)} connections to database! ({len(connections_db)} per user)")
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
        user_ids = await seed_user_data(engine=engine, num_users=2)
        world_ids = await seed_world_data(engine=engine, user_ids=user_ids)
        await seed_account_data(engine=engine, user_ids=user_ids)

        # Seed in dependency order, passing user_ids and world_ids
        await seed_player_data(engine=engine, user_ids=user_ids, world_ids=world_ids)
        await seed_character_data(engine=engine, user_ids=user_ids, world_ids=world_ids)
        await seed_encounter_data(engine=engine, user_ids=user_ids, world_ids=world_ids)
        await seed_memory_data(engine=engine, user_ids=user_ids, world_ids=world_ids)
        await seed_reveal_data(engine=engine, user_ids=user_ids, world_ids=world_ids)
        await seed_connection_data(engine=engine, user_ids=user_ids, world_ids=world_ids)

        logger.info(f"✅ All data seeded for {len(user_ids)} users!")
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