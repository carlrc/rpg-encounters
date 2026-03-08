#!/usr/bin/env python3
import argparse
import asyncio
import json
import sys
from pathlib import Path

from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine

# Ensure "backend" root is on sys.path when executed as a script.
BACKEND_ROOT = Path(__file__).resolve().parents[2]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.auth.session import SESSION_CONFIG  # noqa: E402
from app.data.account_store import AccountStore  # noqa: E402
from app.data.magic_link_store import MagicLinkStore  # noqa: E402
from app.data.user_store import UserStore  # noqa: E402
from app.data.world_store import WorldStore  # noqa: E402
from app.http import DEVICE_NONCE_COOKIE  # noqa: E402
from app.main import app  # noqa: E402
from app.models.account import AccountCreate  # noqa: E402
from app.models.magic_link import MagicLinkCreate  # noqa: E402
from app.models.user import UserCreate  # noqa: E402
from app.utils import get_or_throw  # noqa: E402
from tests.fixtures.seed_data import seed_all_data  # noqa: E402
from tests.utilities import set_user_billing_state  # noqa: E402


def _fail(message: str) -> None:
    print(message, file=sys.stderr)
    raise SystemExit(1)


async def _ensure_seeded_dm(email: str) -> tuple[int, int]:
    account = await AccountStore(user_id=None).get_by_email(email)
    if account:
        worlds = await WorldStore(user_id=account.user_id).get_all()
        if worlds:
            return account.user_id, worlds[0].id

    user = await UserStore().create(UserCreate())
    await AccountStore(user_id=user.id).create(
        AccountCreate(user_id=user.id, email=email)
    )
    world = await WorldStore(user_id=user.id).create()

    engine = create_async_engine(get_or_throw("DATABASE_URL"))
    await seed_all_data(engine=engine, user_ids=[user.id], world_ids=[world.id])
    return user.id, world.id


async def _bootstrap_seeded_dm_session(email: str) -> dict[str, int | str]:
    user_id, world_id = await _ensure_seeded_dm(email)
    await set_user_billing_state(
        user_id=user_id,
        available_tokens=5000,
        last_used_tokens=0,
        total_used_tokens=0,
    )

    raw_token = MagicLinkStore.generate_token()
    device_nonce = MagicLinkStore.generate_token()
    magic_link = MagicLinkCreate(
        user_id=user_id,
        token_hash=MagicLinkStore.hash_token(raw_token),
        device_nonce_hash=MagicLinkStore.hash_token(device_nonce),
        expires_at=MagicLinkStore.magic_link_expiry(),
        used=False,
    )
    await MagicLinkStore(user_id=user_id).create(magic_link)

    client = TestClient(app)
    client.cookies.set(DEVICE_NONCE_COOKIE, device_nonce)
    response = client.get(f"/api/auth?token={raw_token}", follow_redirects=False)
    if response.status_code != 200:
        _fail(
            f"Failed to consume magic link for seeded DM '{email}'. "
            f"Status={response.status_code}, Body={response.text.strip()}"
        )

    session_cookie_name = SESSION_CONFIG.session_cookie_name
    session_cookie_value = client.cookies.get(session_cookie_name)
    if not session_cookie_value:
        _fail(
            "Magic link consume succeeded but no session cookie was issued by backend. "
            f"Expected cookie '{session_cookie_name}'."
        )

    return {
        "cookie_name": session_cookie_name,
        "cookie_value": session_cookie_value,
        "world_id": world_id,
        "user_id": user_id,
        "email": email,
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Bootstrap a DM session for Playwright."
    )
    parser.add_argument(
        "--email", required=True, help="Seeded DM email for this test run."
    )
    args = parser.parse_args()
    email = args.email
    try:
        payload = asyncio.run(_bootstrap_seeded_dm_session(email))
    except SystemExit:
        raise
    except Exception as error:
        _fail(
            "Failed to bootstrap seeded DM session. Ensure local backend dependencies "
            f"(especially Postgres) are running and seeded. Root error: {error}"
        )
    # Stdout must contain JSON only for machine parsing by Playwright global setup.
    print(json.dumps(payload))


if __name__ == "__main__":
    main()
