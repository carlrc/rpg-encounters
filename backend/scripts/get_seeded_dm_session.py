#!/usr/bin/env python3
import asyncio
import json
import os
import sys
from pathlib import Path

from fastapi.testclient import TestClient

from app.auth.session import SESSION_CONFIG
from app.data.account_store import AccountStore
from app.data.magic_link_store import MagicLinkStore
from app.data.world_store import WorldStore
from app.http import DEVICE_NONCE_COOKIE
from app.main import app
from app.models.magic_link import MagicLinkCreate

# Ensure "backend" root is on sys.path when executed as a script.
BACKEND_ROOT = Path(__file__).resolve().parent.parent
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

DEFAULT_DM_EMAIL = "test1@example.com"


def _fail(message: str) -> None:
    print(message, file=sys.stderr)
    raise SystemExit(1)


async def _bootstrap_seeded_dm_session(email: str) -> dict[str, int | str]:
    account = await AccountStore(user_id=None).get_by_email(email)
    if not account:
        _fail(
            f"Seeded DM account '{email}' not found. Run existing seeding first: "
            "python -m tests.fixtures.seed_data"
        )

    worlds = await WorldStore(user_id=account.user_id).get_all()
    if not worlds:
        _fail(
            f"No worlds found for seeded DM '{email}' (user_id={account.user_id}). "
            "Run existing seeding first: python -m tests.fixtures.seed_data"
        )
    world = worlds[0]

    raw_token = MagicLinkStore.generate_token()
    device_nonce = MagicLinkStore.generate_token()
    magic_link = MagicLinkCreate(
        user_id=account.user_id,
        token_hash=MagicLinkStore.hash_token(raw_token),
        device_nonce_hash=MagicLinkStore.hash_token(device_nonce),
        expires_at=MagicLinkStore.magic_link_expiry(),
        used=False,
    )
    await MagicLinkStore(user_id=account.user_id).create(magic_link)

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
        "world_id": world.id,
        "user_id": account.user_id,
        "email": email,
    }


def main() -> None:
    email = os.getenv("PLAYWRIGHT_SEEDED_DM_EMAIL", DEFAULT_DM_EMAIL)
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
