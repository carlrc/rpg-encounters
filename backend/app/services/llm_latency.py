import asyncio
import logging
from contextlib import asynccontextmanager, suppress
from typing import AsyncIterator

from fastapi import WebSocket

from app.utils import get_or_throw

logger = logging.getLogger(__name__)

LLM_IDEAL_LATENCY_SECONDS = float(get_or_throw("LLM_IDEAL_LATENCY_SECONDS"))
DEFAULT_MODEL_NAME = get_or_throw("DEFAULT_MODEL_NAME")


@asynccontextmanager
async def llm_latency_notice(websocket: WebSocket) -> AsyncIterator[None]:
    finished = asyncio.Event()
    notified = asyncio.Event()

    async def _timer() -> None:
        try:
            await asyncio.sleep(LLM_IDEAL_LATENCY_SECONDS)
            if finished.is_set():
                # LLM completed before threshold; skip the slow notice.
                return
            notified.set()
            await websocket.send_json(
                {
                    "type": "llm_slow",
                    "model": DEFAULT_MODEL_NAME,
                }
            )
        except asyncio.CancelledError:
            return
        except Exception as e:
            logger.error("Failed to send llm_slow notice: %s", e)

    # Run the slow-notice timer in the background and guarantee cleanup on exit.
    timer_task = asyncio.create_task(_timer())
    try:
        yield
    finally:
        # Mark completion so the timer won't send a late notice.
        finished.set()
        if not timer_task.done():
            if notified.is_set():
                # Timer already fired; let it finish sending the notice.
                with suppress(asyncio.CancelledError):
                    await timer_task
            else:
                # Cancel pending timer task and swallow cancellation noise.
                timer_task.cancel()
                with suppress(asyncio.CancelledError):
                    await timer_task
