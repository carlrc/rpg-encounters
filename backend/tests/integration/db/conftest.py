#!/usr/bin/env python3
import os

import pytest
from dotenv import load_dotenv
from sqlalchemy import create_engine

from app.db.init_db import create_tables, drop_tables
from tests.fixtures.seed_data import seed_user_data, seed_world_data


@pytest.fixture(autouse=True)
def integration_db_setup():
    """Setup and teardown database for integration tests"""
    load_dotenv()
    url = os.getenv("TEST_DATABASE_URL")
    engine = create_engine(url)
    create_tables(engine=engine)
    seed_user_data(engine=engine)
    seed_world_data(engine=engine)
    yield
    drop_tables(engine=engine)
