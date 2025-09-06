import hashlib
import logging
import secrets
from datetime import datetime, timedelta, timezone

from sqlalchemy import and_, delete, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.data.base_store import BaseStore
from app.db.models.magic_link import MagicLinkORM
from app.models.magic_link import MagicLink, MagicLinkCreate

logger = logging.getLogger(__name__)


class MagicLinkStore(BaseStore):
    def __init__(
        self,
        user_id: int = 0,
        world_id: int | None = None,
        session: AsyncSession | None = None,
    ):
        # Magic links don't need user_id for creation, but keep consistent with BaseStore
        super().__init__(user_id, world_id, session)

    def generate_token(self, nbytes: int = 32) -> str:  # cspell:disable-line
        """Generate a random URL-safe token"""
        return secrets.token_urlsafe(nbytes)  # cspell:disable-line

    def hash_token(self, token: str) -> str:
        """Generate SHA-256 hash of token"""
        return hashlib.sha256(token.encode("utf-8")).hexdigest()

    def magic_link_expiry(self, minutes: int = 10) -> datetime:
        """Calculate expiry time for magic link"""
        return datetime.now(timezone.utc) + timedelta(minutes=minutes)

    async def create(self, data: MagicLinkCreate) -> MagicLink:
        """Create a new magic link"""
        try:
            async with self.get_session() as session:
                magic_link = MagicLinkORM(**data.model_dump())
                session.add(magic_link)
                await session.flush()
                await session.refresh(magic_link)
                return MagicLink.model_validate(magic_link)
        except SQLAlchemyError as e:
            logger.error(f"Error creating magic link for user {data.user_id}: {e}")
            raise

    async def get_by_token_hash(self, token_hash: str) -> MagicLink | None:
        """Get magic link by token hash"""
        try:
            async with self.get_session() as session:
                result = await session.execute(
                    select(MagicLinkORM).where(MagicLinkORM.token_hash == token_hash)
                )
                magic_link = result.scalar_one_or_none()
                return MagicLink.model_validate(magic_link) if magic_link else None
        except SQLAlchemyError as e:
            logger.error(f"Error getting magic link by token hash: {e}")
            raise

    async def mark_used(self, token_hash: str) -> bool:
        """Mark a magic link as used"""
        try:
            async with self.get_session() as session:
                result = await session.execute(
                    select(MagicLinkORM).where(
                        and_(
                            MagicLinkORM.token_hash == token_hash,
                            MagicLinkORM.used == False,  # noqa: E712
                            MagicLinkORM.expires_at > datetime.now(timezone.utc),
                        )
                    )
                )
                magic_link = result.scalar_one_or_none()
                if magic_link:
                    magic_link.used = True
                    magic_link.used_at = datetime.now(timezone.utc)
                    await session.flush()
                    return True
                return False
        except SQLAlchemyError as e:
            logger.error(f"Error marking magic link as used: {e}")
            raise

    async def cleanup_expired(self) -> int:
        """Delete expired and used magic links. Returns count of deleted records."""
        try:
            async with self.get_session() as session:
                cutoff_time = datetime.now(timezone.utc) - timedelta(days=1)
                result = await session.execute(
                    delete(MagicLinkORM).where(
                        (MagicLinkORM.expires_at < datetime.now(timezone.utc))
                        | (MagicLinkORM.used == True)  # noqa: E712
                        | (MagicLinkORM.created_at < cutoff_time)
                    )
                )
                await session.flush()
                return result.rowcount or 0
        except SQLAlchemyError as e:
            logger.error(f"Error cleaning up expired magic links: {e}")
            raise

    async def is_valid_token(
        self, token_hash: str, device_nonce_hash: str
    ) -> tuple[bool, MagicLink | None]:
        """
        Check if token is valid for consumption.
        Returns (is_valid, magic_link_data)
        Note: device_nonce_hash validation is done at router level
        """
        magic_link = await self.get_by_token_hash(token_hash)
        if not magic_link:
            return False, None

        now = datetime.now(timezone.utc)

        # Check all validation criteria
        if magic_link.used or magic_link.expires_at <= now:
            return False, magic_link

        return True, magic_link
