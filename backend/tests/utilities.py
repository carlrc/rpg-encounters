from sqlalchemy.ext.asyncio import create_async_engine

from app.data.account_store import AccountStore
from app.data.user_billing_store import UserBillingStore
from app.db.init_db import create_tables, drop_tables
from app.models.user_billing import UserBillingUpdate
from app.services.user_token import UserTokenService
from app.utils import get_or_throw
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
    url = get_or_throw("TEST_DATABASE_URL")
    async_engine = create_async_engine(url)
    await create_tables(engine=async_engine)
    user_ids = await seed_user_data(engine=async_engine)
    await seed_world_data(user_ids=user_ids, engine=async_engine)
    return async_engine


async def teardown_test_database(async_engine):
    """Teardown test database"""
    await drop_tables(engine=async_engine)


async def get_user_id_by_email(email: str) -> int:
    account = await AccountStore(user_id=None).get_by_email(email=email)
    if not account:
        raise RuntimeError(
            f"Account with email '{email}' was not found. Seed test data first."
        )
    return account.user_id


async def set_user_billing_state(
    user_id: int,
    available_tokens: int,
    last_used_tokens: int,
    total_used_tokens: int | None = None,
) -> None:
    store = UserBillingStore(user_id=user_id)
    existing = await store.get_or_create(user_id=user_id)
    next_total_used = (
        existing.total_used_tokens if total_used_tokens is None else total_used_tokens
    )
    await store.update_by_user_id(
        user_id=user_id,
        user_billing_update=UserBillingUpdate(
            available_tokens=available_tokens,
            last_used_tokens=last_used_tokens,
            total_used_tokens=next_total_used,
        ),
    )
    await UserTokenService().overwrite_cache_from_db(user_id=user_id)
