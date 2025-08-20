import logging
from typing import Callable

from langfuse import get_client
from pydantic_ai import Agent

logger = logging.getLogger(__name__)

TelemetryFunc = Callable[[], None]


def setup_telemetry():
    # Verify langfuse connection
    if get_client().auth_check():
        logger.debug("Langfuse client is authenticated and ready!")
    else:
        raise RuntimeError("Langfuse auth failed.")

    # Initialize Pydantic AI instrumentation
    Agent.instrument_all()
