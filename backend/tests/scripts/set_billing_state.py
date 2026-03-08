#!/usr/bin/env python3
import argparse
import asyncio
import json
import sys
from pathlib import Path

# Ensure "backend" root is on sys.path when executed as a script.
BACKEND_ROOT = Path(__file__).resolve().parents[2]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from tests.utilities import get_user_id_by_email, set_user_billing_state  # noqa: E402


async def run(
    email: str,
    user_id: int | None,
    available: int,
    last_used: int,
    total_used: int | None,
) -> dict[str, int]:
    resolved_user_id = (
        user_id if user_id is not None else await get_user_id_by_email(email)
    )
    await set_user_billing_state(
        user_id=resolved_user_id,
        available_tokens=available,
        last_used_tokens=last_used,
        total_used_tokens=total_used,
    )
    return {
        "user_id": resolved_user_id,
        "available_tokens": available,
        "last_used_tokens": last_used,
        "total_used_tokens": 0 if total_used is None else total_used,
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Set e2e billing state and refresh Redis usage cache."
    )
    target = parser.add_mutually_exclusive_group(required=True)
    target.add_argument(
        "--email",
        type=str,
        help="Seeded user email.",
    )
    target.add_argument(
        "--user-id",
        type=int,
        help="Explicit user ID.",
    )
    parser.add_argument("--available", type=int, required=True)
    parser.add_argument("--last-used", type=int, required=True)
    parser.add_argument("--total-used", type=int, default=None)
    args = parser.parse_args()
    payload = asyncio.run(
        run(
            email=args.email,
            user_id=args.user_id,
            available=args.available,
            last_used=args.last_used,
            total_used=args.total_used,
        )
    )
    print(json.dumps(payload))


if __name__ == "__main__":
    main()
