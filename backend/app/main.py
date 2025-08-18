import logging

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import (
    canvas,
    characters,
    encounters,
    game,
    memories,
    players,
    reveals,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="D&D AI Character Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
    ],  # Vite dev server ports
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(players.router)
app.include_router(characters.router)
app.include_router(memories.router)
app.include_router(reveals.router)
app.include_router(encounters.router)
app.include_router(canvas.router)
app.include_router(game.router)


@app.get("/")
async def root():
    return {"message": "D&D AI Character Backend is running"}


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
