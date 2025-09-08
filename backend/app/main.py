import logging

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from starlette.middleware.sessions import SessionMiddleware

from app.auth.session import SESSION_CONFIG
from app.routers import (
    auth,
    canvas,
    characters,
    encounters,
    game,
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


@app.get("/")
async def root():
    return RedirectResponse(url=f"{FRONTEND_URL}/players", status_code=302)


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True, loop="uvloop")
