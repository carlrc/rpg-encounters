import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.rate_limiter import check_rate_limit
from app.data.character_store import CharacterStore
from app.data.encounter_store import EncounterStore
from app.data.player_magic_link_store import (
    PlayerMagicLinkStore,
    PlayerTokenAlreadyUsedError,
    PlayerTokenExpiredError,
    PlayerTokenNotFoundError,
)
from app.data.player_store import PlayerStore
from app.db.connection import get_async_db_routes_session
from app.dependencies import validate_current_player, validate_current_user_world
from app.http import ENTITY_NOT_FOUND, INTERNAL_SERVER_ERROR
from app.models.encounter import EncounterWithCharacters
from app.models.player import Player, PlayerCreate, PlayerUpdate
from app.models.player_magic_link import PlayerLoginResponse
from app.utils import get_or_throw

router = APIRouter(prefix="/api/players", tags=["players"])

logger = logging.getLogger(__name__)

FRONTEND_URL = get_or_throw("FRONTEND_URL")
LOG_MAGIC_LINK = get_or_throw("LOG_MAGIC_LINK").lower() == "true"


@router.get("", response_model=List[Player])
async def get_players(
    user_world: tuple[int, int] = Depends(validate_current_user_world),
):
    """Get all players"""
    user_id, world_id = user_world
    try:
        return await PlayerStore(user_id=user_id, world_id=world_id).get_all()
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get players for user {user_id}, world {world_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=INTERNAL_SERVER_ERROR,
        )


@router.get("/{player_id}", response_model=Player)
async def get_player(
    player_id: int, user_world: tuple[int, int] = Depends(validate_current_user_world)
):
    """Get a specific player by ID"""
    user_id, world_id = user_world
    try:
        player = await PlayerStore(user_id=user_id, world_id=world_id).get_by_id(
            player_id
        )
        if player is None:
            raise HTTPException(status_code=404, detail=ENTITY_NOT_FOUND)
        return player
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Failed to get player {player_id} for user {user_id}, world {world_id}: {e}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=INTERNAL_SERVER_ERROR,
        )


@router.post("/", response_model=Player, status_code=201)
async def create_player(
    player: PlayerCreate,
    user_world: tuple[int, int] = Depends(validate_current_user_world),
):
    """Create a new player"""
    user_id, world_id = user_world
    try:
        return await PlayerStore(user_id=user_id, world_id=world_id).create(player)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Failed to create player for user {user_id}, world {world_id}: {e}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=INTERNAL_SERVER_ERROR,
        )


@router.put("/{player_id}", response_model=Player)
async def update_player(
    player_id: int,
    player_update: PlayerUpdate,
    user_world: tuple[int, int] = Depends(validate_current_user_world),
):
    """Update an existing player"""
    user_id, world_id = user_world
    try:
        updated_player = await PlayerStore(user_id=user_id, world_id=world_id).update(
            player_id, player_update
        )
        if updated_player is None:
            raise HTTPException(status_code=404, detail=ENTITY_NOT_FOUND)
        return updated_player
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Failed to update player {player_id} for user {user_id}, world {world_id}: {e}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=INTERNAL_SERVER_ERROR,
        )


@router.delete("/{player_id}", status_code=204)
async def delete_player(
    player_id: int, user_world: tuple[int, int] = Depends(validate_current_user_world)
):
    """Delete a player"""
    user_id, world_id = user_world
    try:
        if not await PlayerStore(user_id=user_id, world_id=world_id).delete(player_id):
            raise HTTPException(status_code=404, detail=ENTITY_NOT_FOUND)
        return None
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Failed to delete player {player_id} for user {user_id}, world {world_id}: {e}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=INTERNAL_SERVER_ERROR,
        )


@router.post("/{player_id}/login", response_model=PlayerLoginResponse)
async def request_player_login(
    player_id: int,
    user_world: tuple[int, int] = Depends(validate_current_user_world),
    session: AsyncSession = Depends(get_async_db_routes_session),
):
    """Generate a magic link for player login"""
    user_id, world_id = user_world
    try:
        # Verify player exists and belongs to this user's world
        player = await PlayerStore(user_id=user_id, world_id=world_id).get_by_id(
            player_id
        )
        if not player:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=ENTITY_NOT_FOUND
            )

        # Create player magic link
        player_magic_link_store = PlayerMagicLinkStore(session=session)
        player_magic_link, raw_token = await player_magic_link_store.create(
            player_id=player_id, user_id=user_id, world_id=world_id
        )

        # Login link
        magic_link = f"{FRONTEND_URL}/players/{player_id}/login?token={raw_token}"

        # So you can see it when running locally
        if LOG_MAGIC_LINK:
            logger.info(f"User {user_id} & player {player_id} login link: {magic_link}")

        return PlayerLoginResponse(
            login_url=magic_link, expires_at=player_magic_link.expires_at
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Failed to generate login link for player {player_id}, user {user_id}, world {world_id}: {e}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=INTERNAL_SERVER_ERROR,
        )


@router.get("/{player_id}/login")
async def consume_player_login(
    player_id: int,
    token: str,
    request: Request,
    session: AsyncSession = Depends(get_async_db_routes_session),
):
    """Consume a player magic link token to create a player session"""
    # Rate limit by IP address to prevent spamming
    client_ip = request.client.host if request.client else "unknown"
    if not await check_rate_limit(client_ip, max_count=50, window_minutes=10):
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS)

    try:
        # Validate and consume magic link
        player_magic_link_store = PlayerMagicLinkStore(session=session)
        token_hash = PlayerMagicLinkStore.hash_token(token)

        player_magic_link = await player_magic_link_store.consume(token_hash)

        # Verify the player_id matches the URL parameter
        if player_magic_link.player_id != player_id:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

        # Create player session
        request.session["user_id"] = player_magic_link.user_id
        request.session["player_id"] = player_magic_link.player_id
        request.session["world_id"] = player_magic_link.world_id

        # TODO: Should be pydantic model
        # Return world_id so frontend can set world store immediately
        return {"world_id": player_magic_link.world_id}

    except (
        PlayerTokenNotFoundError,
        PlayerTokenAlreadyUsedError,
        PlayerTokenExpiredError,
    ) as e:
        logger.warning(f"Invalid login attempt for player {player_id}: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to consume player login for player {player_id}: {e}")
        raise HTTPException(status_code=500, detail=INTERNAL_SERVER_ERROR)


@router.get("/{player_id}/encounter", response_model=EncounterWithCharacters)
async def get_player_encounter(
    player_id: int,
    player_info: tuple[int, int, int] = Depends(validate_current_player),
    session: AsyncSession = Depends(get_async_db_routes_session),
):
    """Get the encounter assigned to the current player with character details"""
    session_player_id, user_id, world_id = player_info

    # Verify the requested player_id matches the session player_id
    if session_player_id != player_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    try:
        # Get the encounter where this player is assigned
        player_encounter = await EncounterStore(
            user_id=user_id, world_id=world_id, session=session
        ).get_by_player(player_id)

        if not player_encounter:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Player is not assigned to any encounter",
            )

        # Fetch character details for all characters in the encounter
        characters = []
        character_store = CharacterStore(
            user_id=user_id, world_id=world_id, session=session
        )
        if player_encounter.character_ids:
            for character_id in player_encounter.character_ids:
                character = await character_store.get_by_id(character_id)
                if character:
                    characters.append(character)

        # Build the response with character details
        return EncounterWithCharacters(
            id=player_encounter.id,
            name=player_encounter.name,
            description=player_encounter.description,
            position_x=player_encounter.position_x,
            position_y=player_encounter.position_y,
            character_ids=player_encounter.character_ids,
            player_ids=player_encounter.player_ids,
            world_id=world_id,
            characters=characters,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Failed to get encounters for player {player_id}, user {user_id}, world {world_id}: {e}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=INTERNAL_SERVER_ERROR,
        )
