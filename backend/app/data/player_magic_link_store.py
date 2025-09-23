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
        user_id: int = 0,
        world_id: int | None = None,
        session: AsyncSession | None = None,
    ):
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
        """Generate expiry time for magic link (default 10 minutes)"""
        return datetime.now(timezone.utc) + timedelta(minutes=minutes)

    async def create(
        self, player_id: int, user_id: int, world_id: int
    ) -> tuple[PlayerMagicLink, str]:
        """Create a new player magic link and return both the link and raw token"""
        try:
            raw_token = self.generate_token()
            token_hash = self.hash_token(raw_token)

            player_magic_link_data = PlayerMagicLinkCreate(
                player_id=player_id,
                user_id=user_id,
                world_id=world_id,
                token_hash=token_hash,
                expires_at=self.magic_link_expiry(),
                used=False,
            )

            player_magic_link_orm = PlayerMagicLinkORM(
                **player_magic_link_data.model_dump()
            )
            self.session.add(player_magic_link_orm)
            await self.session.flush()
            await self.session.refresh(player_magic_link_orm)

            player_magic_link = PlayerMagicLink.model_validate(player_magic_link_orm)
            return player_magic_link, raw_token

        except Exception as e:
            logger.error(
                f"Failed to create player magic link for player {player_id}: {e}"
            )
            raise e

    async def consume(self, token_hash: str) -> PlayerMagicLink:
        """
        Validate and consume a player magic link token in a single atomic operation.
        Returns the PlayerMagicLink if successful.
        """
        try:
            result = await self.session.execute(
                select(PlayerMagicLinkORM).where(
                    PlayerMagicLinkORM.token_hash == token_hash
                )
            )
            player_magic_link_orm = result.scalar_one_or_none()

            if not player_magic_link_orm:
                raise PlayerTokenNotFoundError("Player magic link token not found")

            if player_magic_link_orm.used:
                raise PlayerTokenAlreadyUsedError(
                    "Player magic link token already used"
                )

            if player_magic_link_orm.expires_at < datetime.now(timezone.utc):
                raise PlayerTokenExpiredError("Player magic link token expired")

            # Mark as used atomically
            await self.session.execute(
                update(PlayerMagicLinkORM)
                .where(PlayerMagicLinkORM.id == player_magic_link_orm.id)
                .values(used=True, used_at=datetime.now(timezone.utc))
            )

            await self.session.flush()
            await self.session.refresh(player_magic_link_orm)

            return PlayerMagicLink.model_validate(player_magic_link_orm)

        except Exception as e:
            logger.error(f"Failed to consume player magic link token: {e}")
            raise e
