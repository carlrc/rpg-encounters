import logging

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from app.auth.session import IS_LOCAL, SESSION_CONFIG
from app.routers import (
    auth,
    canvas,
    characters,
    encounters,
    game,
    health,
    memories,
    players,
    reveals,
    voices,
    worlds,
)
from app.telemetry import setup_telemetry
from app.utils import get_or_throw

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="RPG Encounters")

FRONTEND_URL = get_or_throw("FRONTEND_URL")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add session middleware
app.add_middleware(
    SessionMiddleware,
    secret_key=SESSION_CONFIG.secret_key,
    session_cookie=SESSION_CONFIG.session_cookie_name,
    max_age=SESSION_CONFIG.max_age,
    https_only=SESSION_CONFIG.secure,
)

app.include_router(health.router)
app.include_router(auth.router)
app.include_router(players.router)
app.include_router(characters.router)
app.include_router(memories.router)
app.include_router(reveals.router)
app.include_router(encounters.router)
app.include_router(canvas.router)
app.include_router(game.router)
app.include_router(voices.router)
app.include_router(worlds.router)

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
