import logging
import os

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from app.auth.session import get_session_middleware
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

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="RPG Encounters")

FRONTEND_URL = os.getenv("FRONTEND_URL")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add session middleware
app.add_middleware(
    get_session_middleware(),
    secret_key=os.getenv("SESSION_SECRET_KEY", "dev-secret-change-in-production"),
    session_cookie="session",
    max_age=60 * 60 * 24 * 7,  # 7 days
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
