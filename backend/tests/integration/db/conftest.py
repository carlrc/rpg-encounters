#!/usr/bin/env python3
import os

import pytest_asyncio
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine

from app.db.init_db import create_tables, drop_tables
from tests.fixtures.seed_data import seed_user_data, seed_world_data


@pytest_asyncio.fixture(autouse=True)
async def integration_db_setup():
    """Setup and teardown database for integration tests"""
    load_dotenv()
    url = os.getenv("TEST_DATABASE_URL")
    async_engine = create_async_engine(url)
    await create_tables(engine=async_engine)
    await seed_user_data(engine=async_engine)
    await seed_world_data(engine=async_engine)
    yield
    await drop_tables(engine=async_engine)
