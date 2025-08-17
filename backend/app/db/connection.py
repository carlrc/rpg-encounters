import os

from dotenv import load_dotenv
from sqlalchemy import create_engine

# Load environment variables from .env file
load_dotenv()

PLAYERS_TABLE = "players"
CHARACTERS_TABLE = "characters"
MEMORIES_TABLE = "memories"
REVEALS_TABLE = "reveals"
INFLUENCES_TABLE = "influences"
ENCOUNTERS_TABLE = "encounters"
CONNECTIONS_TABLE = "connections"

# Environment-based database configuration
DATABASE_URL = os.getenv("DATABASE_URL")

DB_ENGINE = create_engine(DATABASE_URL)
