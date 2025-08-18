#!/usr/bin/env python3
import pytest
from dotenv import load_dotenv

from app.db.init_db import create_tables, drop_tables
from tests.fixtures.migrate_data import seed_user_data, seed_world_data


@pytest.fixture(autouse=True)
def integration_db_setup():
    """Setup and teardown database for integration tests"""
    load_dotenv()
    create_tables(use_test_db=True)
    seed_user_data(use_test_db=True)
    seed_world_data(use_test_db=True)
    yield
    drop_tables(use_test_db=True)
