from __future__ import annotations

from logging.config import fileConfig

from dotenv import load_dotenv
from sqlalchemy import Connection, pool
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context

# Import ORM models/association tables so metadata is fully registered.
from app.db.models.account import AccountORM  # noqa: F401
from app.db.models.associations import (  # noqa: F401
    encounter_characters,
    encounter_players,
    memory_characters,
    reveal_characters,
)
from app.db.models.base import SimpleBase, UnifiedBase
from app.db.models.character import CharacterORM  # noqa: F401
from app.db.models.connection import ConnectionORM  # noqa: F401
from app.db.models.conversation import ConversationORM  # noqa: F401
from app.db.models.encounter import EncounterORM  # noqa: F401
from app.db.models.influence import InfluenceORM  # noqa: F401
from app.db.models.magic_link import MagicLinkORM  # noqa: F401
from app.db.models.memory import MemoryORM  # noqa: F401
from app.db.models.moderation import ModerationORM  # noqa: F401
from app.db.models.player import PlayerORM  # noqa: F401
from app.db.models.player_magic_link import PlayerMagicLinkORM  # noqa: F401
from app.db.models.reveal import RevealORM  # noqa: F401
from app.db.models.user import UserORM  # noqa: F401
from app.db.models.user_billing import UserBillingORM  # noqa: F401
from app.db.models.world import WorldORM  # noqa: F401
from app.utils import get_or_throw

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

load_dotenv()
config.set_main_option("sqlalchemy.url", get_or_throw("DATABASE_URL"))

target_metadata = [SimpleBase.metadata, UnifiedBase.metadata]

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    """Bind Alembic context to an active connection and execute pending migrations."""
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in online mode by connecting to the database and executing DDL.

    Offline mode only renders SQL text; this path applies migrations directly.
    """
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async def run_async_migrations() -> None:
        async with connectable.connect() as connection:
            await connection.run_sync(do_run_migrations)
        await connectable.dispose()

    import asyncio

    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
