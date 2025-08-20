import logging

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from langfuse import get_client
from pydantic_ai.agent import Agent

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
        "http://localhost:3001",
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

# Verify langfuse connection
if get_client().auth_check():
    logger.debug("Langfuse client is authenticated and ready!")
else:
    raise RuntimeError("Langfuse auth failed.")

# Initialize Pydantic AI instrumentation
Agent.instrument_all()


@app.get("/")
async def root():
    return {"message": "D&D AI Character Backend is running"}


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
