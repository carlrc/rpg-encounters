from fastapi import WebSocket

INSUFFICIENT_TOKENS_TYPE = "billing_error"
INSUFFICIENT_TOKENS_CODE = "INSUFFICIENT_TOKENS"
INSUFFICIENT_TOKENS_MESSAGE = "Insufficient tokens"


async def send_insufficient_tokens_response(websocket: WebSocket) -> None:
    await websocket.send_json(
        {
            "type": INSUFFICIENT_TOKENS_TYPE,
            "code": INSUFFICIENT_TOKENS_CODE,
            "message": INSUFFICIENT_TOKENS_MESSAGE,
        }
    )
