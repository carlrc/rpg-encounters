#!/usr/bin/env python3
"""End-to-end test configuration"""
import pytest_asyncio

from tests.utilities import setup_test_database, teardown_test_database


@pytest_asyncio.fixture(autouse=True)
async def end_to_end_setup():
    """Setup and teardown database for end-to-end tests"""
    async_engine = await setup_test_database()
    yield
    await teardown_test_database(async_engine)
