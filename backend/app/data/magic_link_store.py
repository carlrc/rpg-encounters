import hashlib
import logging
import secrets
from datetime import datetime, timedelta, timezone

from sqlalchemy import delete, select, update
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.data.base_store import BaseStore
from app.db.models.magic_link import MagicLinkORM
from app.models.magic_link import MagicLink, MagicLinkCreate

logger = logging.getLogger(__name__)


class TokenNotFoundError(Exception):
    """Token was not found in database"""

    pass


class TokenExpiredError(Exception):
    """Token has expired"""

    pass


class TokenAlreadyUsedError(Exception):
    """Token has already been used"""

    pass


class DeviceMismatchError(Exception):
    """Device nonce doesn't match the one that requested the token"""

    pass


class MagicLinkStore(BaseStore):
    def __init__(
        self,
        user_id: int = 0,
        world_id: int | None = None,
        session: AsyncSession | None = None,
    ):
        # Magic links don't need user_id for creation, but keep consistent with BaseStore
        super().__init__(user_id, world_id, session)

    @staticmethod
    def generate_token(num_bytes: int = 32) -> str:
        """Generate a random URL-safe token"""
        return secrets.token_urlsafe(num_bytes)

    @staticmethod
    def hash_token(token: str) -> str:
        """Generate SHA-256 hash of token"""
        return hashlib.sha256(token.encode("utf-8")).hexdigest()

    @staticmethod
    def magic_link_expiry(minutes: int = 10) -> datetime:
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

    async def consume(
        self, token_hash: str, device_nonce_hash: str
    ) -> MagicLink | None:
        """
        Atomically validate and consume a magic link token with device binding.

        Uses a conditional UPDATE to ensure only valid, unused tokens from the correct
        device are consumed. Multiple concurrent requests will result in only one success.

        Returns the MagicLink if successful.
        Raises specific exceptions for different error conditions.
        """
        try:
            async with self.get_session() as session:
                now = datetime.now(timezone.utc)

                result = await session.execute(
                    update(MagicLinkORM)
                    .where(
                        MagicLinkORM.token_hash == token_hash,
                        MagicLinkORM.used is False,
                        MagicLinkORM.expires_at > now,
                        MagicLinkORM.device_nonce_hash == device_nonce_hash,
                    )
                    .values(used=True, used_at=now)
                    .returning(MagicLinkORM)
                )

                # Extract the updated token - None if no rows matched all conditions
                magic_link = result.scalar_one_or_none()

                if not magic_link:
                    # Conditional update failed - determine specific cause for error message
                    # This diagnostic query is read-only and safe for error reporting
                    check_result = await session.execute(
                        select(MagicLinkORM).where(
                            MagicLinkORM.token_hash == token_hash
                        )
                    )
                    existing_token = check_result.scalar_one_or_none()

                    # Check each possible failure condition in priority order
                    if not existing_token:
                        raise TokenNotFoundError("Token not found")
                    elif existing_token.used:
                        logger.debug(
                            f"User {existing_token.user_id} already used token {existing_token.id}."
                        )
                        raise TokenAlreadyUsedError("Token has already been used")
                    elif existing_token.expires_at <= now:
                        logger.debug(
                            f"User {existing_token.user_id} tried to use expired token {existing_token.id}."
                        )
                        raise TokenExpiredError("Token has expired")
                    elif existing_token.device_nonce_hash != device_nonce_hash:
                        logger.debug(
                            f"User {existing_token.user_id} tried to use a new device with token {existing_token.id}"
                        )
                        raise DeviceMismatchError(
                            "Device mismatch - please use the same device that requested the magic link"
                        )
                    else:
                        # Fallback for unexpected state
                        raise TokenNotFoundError("Token not found")

                # Token successfully consumed
                await session.flush()
                return MagicLink.model_validate(magic_link)
        except (
            TokenNotFoundError,
            TokenAlreadyUsedError,
            TokenExpiredError,
            DeviceMismatchError,
        ):
            raise
        except SQLAlchemyError as e:
            logger.error(f"Error consuming magic link for user {self.user_id}: {e}")
            raise

    async def cleanup(self) -> int:
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
            logger.error(
                f"Error cleaning up expired magic links for user {self.user_id}: {e}"
            )
            raise
