import asyncio
import importlib
import os


class FakeWebSocket:
    def __init__(self) -> None:
        self.sent: list[dict] = []

    async def send_json(self, payload: dict) -> None:
        self.sent.append(payload)


def load_llm_latency_module(ideal_seconds: float, provider: str):
    os.environ["LLM_IDEAL_LATENCY_SECONDS"] = str(ideal_seconds)
    os.environ["DEFAULT_MODEL_NAME"] = provider
    from app.utils import get_or_throw

    get_or_throw.cache_clear()
    import app.services.llm_latency as llm_latency

    return importlib.reload(llm_latency)


async def wait_for_notice(ws: FakeWebSocket, timeout: float = 0.5) -> None:
    async def _poll() -> None:
        while not ws.sent:
            await asyncio.sleep(0.01)

    await asyncio.wait_for(_poll(), timeout=timeout)


async def test_llm_latency_notice_fires():
    llm_latency = load_llm_latency_module(ideal_seconds=0.05, provider="TestModel")
    ws = FakeWebSocket()

    async with llm_latency.llm_latency_notice(ws):
        await wait_for_notice(ws)

    assert len(ws.sent) == 1
    assert ws.sent[0]["type"] == "llm_slow"
    assert ws.sent[0]["model"] == "TestModel"


async def test_llm_latency_notice_does_not_fire_before_threshold():
    llm_latency = load_llm_latency_module(ideal_seconds=0.05, provider="TestModel")
    ws = FakeWebSocket()

    async with llm_latency.llm_latency_notice(ws):
        await asyncio.sleep(0.02)

    assert ws.sent == []
