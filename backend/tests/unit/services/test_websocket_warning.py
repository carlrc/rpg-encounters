from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from app.services.websocket import send_warning_and_close


@pytest.mark.asyncio
async def test_send_warning_and_close_sends_payload_and_closes():
    websocket = SimpleNamespace(
        send_json=AsyncMock(),
        send_text=AsyncMock(),
        close=AsyncMock(),
    )

    await send_warning_and_close(websocket=websocket, message="Warning message")

    websocket.send_json.assert_awaited_once_with(
        {"type": "warning", "message": "Warning message"}
    )
    websocket.send_text.assert_awaited_once_with("AUDIO_COMPLETE")
    websocket.close.assert_awaited_once_with(code=1011, reason="end_of_stream")
