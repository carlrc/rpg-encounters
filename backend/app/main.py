import importlib
import logging
import os
from contextlib import asynccontextmanager
from typing import Callable

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

import os

from app.auth.session import IS_LAN, IS_LOCAL, SESSION_CONFIG
from app.clients.redis_client import validate_redis_connection
from app.routers import (
    auth,
    canvas,
    characters,
    encounters,
    game,
    internal_test,
    memories,
    players,
    profile,
    reveals,
    voices,
    worlds,
)
from app.services.redis import (
    start_token_usage_sync_poller,
    stop_token_usage_sync_poller,
)
from app.telemetry import setup_telemetry
from app.utils import get_or_throw

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def app_lifespan(app: FastAPI):
    await validate_redis_connection()
    start_token_usage_sync_poller(app=app)
    try:
        yield
    finally:
        await stop_token_usage_sync_poller(app=app)


RegisterFn = Callable[[FastAPI], object]


def load_extensions_from_env() -> list[RegisterFn]:
    spec = os.getenv("EXTENSIONS", "").strip()
    if not spec:
        logger.info("No extensions detected...")
        return []

    exts: list[RegisterFn] = []
    for item in (s.strip() for s in spec.split(",") if s.strip()):
        mod_name, fn_name = item.split(":", 1)

        try:
            mod = importlib.import_module(mod_name)
        except ModuleNotFoundError:
            logger.error(f"Extension module not found: {mod_name}")
            raise
        except Exception as e:
            logger.error(f"Extension error for {item}. {e}")
            raise

        fn = getattr(mod, fn_name, None)
        if not callable(fn):
            raise ValueError(f"Extension '{item}' is not callable")

        exts.append(fn)

    logger.info("Extensions loaded...")

    return exts


app = FastAPI(
    title="RPG Encounters",
    docs_url=None,
    openapi_url=None,
    redoc_url=None,
    lifespan=app_lifespan,
)

FRONTEND_URL = get_or_throw("FRONTEND_URL")
LAN_PUBLIC_URL = os.getenv("LAN_PUBLIC_URL")

cors_kwargs = {
    "allow_credentials": True,
    "allow_methods": ["*"],
    "allow_headers": ["*"],
}
if IS_LAN and LAN_PUBLIC_URL:
    cors_kwargs["allow_origins"] = [LAN_PUBLIC_URL]
else:
    cors_kwargs["allow_origins"] = [FRONTEND_URL]

app.add_middleware(CORSMiddleware, **cors_kwargs)

# Add session middleware
app.add_middleware(
    SessionMiddleware,
    secret_key=SESSION_CONFIG.secret_key,
    session_cookie=SESSION_CONFIG.session_cookie_name,
    max_age=SESSION_CONFIG.max_age,
    https_only=SESSION_CONFIG.secure,
)

app.include_router(auth.router)
app.include_router(profile.router)
app.include_router(players.router)
app.include_router(characters.router)
app.include_router(memories.router)
app.include_router(reveals.router)
app.include_router(encounters.router)
app.include_router(canvas.router)
app.include_router(game.router)
app.include_router(voices.router)
app.include_router(worlds.router)
if IS_LOCAL:
    app.include_router(internal_test.router)

# Add external extensions
for register in load_extensions_from_env():
    register(app)


@app.get("/internal/health", include_in_schema=False)
async def internal_health_check() -> Response:
    return Response(status_code=200)


setup_telemetry()


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=IS_LOCAL,
        loop="uvloop",
        proxy_headers=True,  # Enable proxy header support for CloudFront/ALB
        forwarded_allow_ips="*",  # Trust forwarded headers from any IP
    )
