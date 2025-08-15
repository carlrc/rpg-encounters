import os

from dotenv import load_dotenv
from sqlalchemy import create_engine

# Load environment variables from .env file
load_dotenv()

PLAYERS_TABLE = "players"
CHARACTERS_TABLE = "characters"
MEMORIES_TABLE = "memories"
REVEALS_TABLE = "reveals"

# Environment-based database configuration
DATABASE_URL = os.getenv("DATABASE_URL")

DB_ENGINE = create_engine(DATABASE_URL)
