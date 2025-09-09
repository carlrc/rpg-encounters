import logging
from typing import Callable

from langfuse import get_client
from pydantic_ai import Agent

from app.utils import get_or_throw

logger = logging.getLogger(__name__)

TelemetryFunc = Callable[[], None]


def setup_telemetry():
    run_telemetry = get_or_throw("LANGFUSE_TRACING_ENABLED")

    if run_telemetry == "false" or run_telemetry == "False":
        logger.info("Skipping telemetry setup...")
        return

    # Check langfuse
    if not get_client().auth_check():
        raise RuntimeError("Langfuse auth failed.")

    # Initialize Pydantic AI instrumentation
    Agent.instrument_all()

    logger.info("Telemetry setup!")
