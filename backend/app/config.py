import os

from app.auth.session import IS_LAN
from app.utils import get_or_throw

FRONTEND_URL = get_or_throw("FRONTEND_URL")
LAN_PUBLIC_URL = os.getenv("LAN_PUBLIC_URL")


def get_public_frontend_url() -> str:
    if IS_LAN and bool(LAN_PUBLIC_URL):
        return LAN_PUBLIC_URL
    else:
        return FRONTEND_URL
