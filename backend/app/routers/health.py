import logging

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.connection import get_async_db_routes_session

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/health", tags=["health"])


@router.get("/")
async def health_check():
    """Basic health check endpoint."""
    return


@router.get("/db")
async def database_health_check(
    session: AsyncSession = Depends(get_async_db_routes_session),
):
    """Health check that includes database connectivity."""
    try:
        # Execute a simple query to test database connection
        result = await session.execute("SELECT 1")
        result.fetchone()
        return
    except Exception as e:
        logger.error(f"Could not connect to db for health check: {e}")
        raise
