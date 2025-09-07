import os

from sqlalchemy.ext.asyncio import create_async_engine

from app.db.init_db import create_tables, drop_tables
from tests.fixtures.seed_data import seed_user_data, seed_world_data


def find_keywords_in_text(text: str, keywords: list) -> list[str]:
    """Helper function to find keywords in text (case-insensitive)."""
    found_keywords = []
    for keyword in keywords:
        if keyword.lower() in text.lower():
            found_keywords.append(keyword)
    return found_keywords


def assert_contains_any_keywords(text: str, keywords: list) -> list[str]:
    found_keywords = find_keywords_in_text(text, keywords)
    assert (
        found_keywords
    ), f"Expected to find at least one keyword from {keywords} in text: {text[:200]}..."
    return found_keywords


def assert_does_not_contain_keywords(text: str, keywords: list) -> list[str]:
    found_keywords = find_keywords_in_text(text, keywords)
    assert (
        not found_keywords
    ), f"Expected to NOT find any keywords from {keywords} in text, but found: {found_keywords}. Text: {text[:200]}..."
    return found_keywords


async def setup_test_database():
    """Setup test database with tables and seed data"""
    url = os.getenv("TEST_DATABASE_URL")
    async_engine = create_async_engine(url)
    await create_tables(engine=async_engine)
    await seed_user_data(engine=async_engine)
    await seed_world_data(engine=async_engine)
    return async_engine


async def teardown_test_database(async_engine):
    """Teardown test database"""
    await drop_tables(engine=async_engine)
