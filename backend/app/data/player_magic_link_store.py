import hashlib
import logging
import secrets
from datetime import datetime, timedelta, timezone

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.data.base_store import BaseStore
from app.db.models.player_magic_link import PlayerMagicLinkORM
from app.models.player_magic_link import (
    PlayerMagicLink,
    PlayerMagicLinkCreate,
)


class PlayerTokenAlreadyUsedError(Exception):
    """Raised when attempting to use an already consumed player magic link token"""


class PlayerTokenExpiredError(Exception):
    """Raised when attempting to use an expired player magic link token"""


class PlayerTokenNotFoundError(Exception):
    """Raised when a player magic link token is not found"""


logger = logging.getLogger(__name__)


class PlayerMagicLinkStore(BaseStore):
    def __init__(
        self,
        user_id: int | None = None,
        world_id: int | None = None,
        session: AsyncSession | None = None,
    ):
        super().__init__(user_id=user_id, world_id=world_id, session=session)

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
        """Generate expiry time for magic link (default 10 minutes)"""
        return datetime.now(timezone.utc) + timedelta(minutes=minutes)

    async def create(
        self, player_magic_link_data: PlayerMagicLinkCreate
    ) -> PlayerMagicLink:
        """Create a new player magic link"""
        try:
            player_magic_link_orm = PlayerMagicLinkORM(
                **player_magic_link_data.model_dump()
            )
            self.session.add(player_magic_link_orm)
            await self.session.flush()
            await self.session.refresh(player_magic_link_orm)

            return PlayerMagicLink.model_validate(player_magic_link_orm)

        except Exception as e:
            logger.error(
                f"Failed to create player magic link for player {player_magic_link_data.player_id}: {e}"
            )
            raise e

    async def consume(self, token_hash: str) -> PlayerMagicLink:
        """
        Atomically validate and consume a player magic link token.

        Uses a conditional UPDATE to ensure only valid, unused tokens are consumed.
        Multiple concurrent requests for the same token will result in only one success.

        Returns the PlayerMagicLink if successful.
        Raises specific exceptions for different error conditions.
        """
        try:
            now = datetime.now(timezone.utc)

            result = await self.session.execute(
                update(PlayerMagicLinkORM)
                .where(
                    PlayerMagicLinkORM.token_hash == token_hash,
                    PlayerMagicLinkORM.used == False,  # noqa: E712
                    PlayerMagicLinkORM.expires_at > now,
                )
                .values(used=True, used_at=now)
                .returning(PlayerMagicLinkORM)
            )

            # Extract the updated token - None if no rows matched the conditions
            player_magic_link_orm = result.scalar_one_or_none()

            if not player_magic_link_orm:
                # The conditional update failed - determine why for specific error message
                # This diagnostic query is safe as it's read-only and not used for business logic
                check_result = await self.session.execute(
                    select(PlayerMagicLinkORM).where(
                        PlayerMagicLinkORM.token_hash == token_hash
                    )
                )
                existing_token = check_result.scalar_one_or_none()

                # Check each possible failure condition
                if not existing_token:
                    raise PlayerTokenNotFoundError("Player magic link token not found")
                elif existing_token.used:
                    raise PlayerTokenAlreadyUsedError(
                        "Player magic link token already used"
                    )
                elif existing_token.expires_at <= now:
                    raise PlayerTokenExpiredError("Player magic link token expired")
                else:
                    # Fallback for unexpected state
                    raise PlayerTokenNotFoundError("Player magic link token not found")

            # Token successfully consumed
            await self.session.flush()
            return PlayerMagicLink.model_validate(player_magic_link_orm)

        except (
            PlayerTokenNotFoundError,
            PlayerTokenAlreadyUsedError,
            PlayerTokenExpiredError,
        ):
            raise
        except Exception as e:
            logger.error(f"Failed to consume player magic link token: {e}")
            raise e
