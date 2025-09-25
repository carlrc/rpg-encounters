import logging
from typing import Dict, List

from fastapi import APIRouter, Depends, HTTPException, WebSocket
from langfuse import get_client, observe
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.session import UserSession
from app.data.connection_store import ConnectionStore
from app.data.encounter_store import EncounterStore
from app.db.connection import get_async_db_routes_session
from app.dependencies import get_websocket_user_world, validate_current_user_world
from app.http import ENTITY_NOT_FOUND, INTERNAL_SERVER_ERROR
from app.models.conversation import ConversationData
from app.models.encounter import Encounter, EncounterCreate, EncounterUpdate
from app.models.encounter_connection import (
    Connection,
    ConnectionCreate,
    ConnectionUpdate,
)
from app.services.challenge import challenge_character
from app.services.context import get_conversation_context
from app.services.conversation import have_conversation
from app.services.reveal_progress import calculate_reveal_progress
from app.utils import get_or_throw

router = APIRouter(prefix="/api/encounters", tags=["encounters"])

logger = logging.getLogger(__name__)


@router.get("/{encounter_id}", response_model=Encounter)
async def get_encounter(
    encounter_id: int,
    session: UserSession = Depends(validate_current_user_world),
):
    """Get a specific encounter by ID"""
    user_id, world_id = session.user_id, session.world_id
    try:
        encounter = await EncounterStore(user_id=user_id, world_id=world_id).get_by_id(
            encounter_id
        )
        if not encounter:
            raise HTTPException(status_code=404, detail=ENTITY_NOT_FOUND)
        return encounter
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Failed to get encounter {encounter_id} for user {user_id}, world {world_id}: {e}"
        )
        raise HTTPException(status_code=500, detail=INTERNAL_SERVER_ERROR)


@router.post("/", response_model=Encounter, status_code=201)
async def create_encounter(
    encounter_data: EncounterCreate,
    session: UserSession = Depends(validate_current_user_world),
):
    """Create a new encounter"""
    user_id, world_id = session.user_id, session.world_id
    try:
        return await EncounterStore(user_id=user_id, world_id=world_id).create(
            encounter_data
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Failed to create encounter for user {user_id}, world {world_id}: {e}"
        )
        raise HTTPException(status_code=500, detail=INTERNAL_SERVER_ERROR)


@router.put("/{encounter_id}", response_model=Encounter)
async def update_encounter(
    encounter_id: int,
    encounter_update: EncounterUpdate,
    session: UserSession = Depends(validate_current_user_world),
):
    """Update an existing encounter"""
    user_id, world_id = session.user_id, session.world_id
    try:
        # Override the ID from the URL path
        encounter_update.id = encounter_id
        encounter = await EncounterStore(user_id=user_id, world_id=world_id).update(
            encounter_id, encounter_update
        )
        if not encounter:
            raise HTTPException(status_code=404, detail=ENTITY_NOT_FOUND)
        return encounter
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Failed to update encounter {encounter_id} for user {user_id}, world {world_id}: {e}"
        )
        raise HTTPException(status_code=500, detail=INTERNAL_SERVER_ERROR)


@router.delete("/{encounter_id}", status_code=204)
async def delete_encounter(
    encounter_id: int,
    session: UserSession = Depends(validate_current_user_world),
):
    """Delete an encounter"""
    user_id, world_id = session.user_id, session.world_id
    try:
        success = await EncounterStore(user_id=user_id, world_id=world_id).delete(
            encounter_id
        )
        if not success:
            raise HTTPException(status_code=404, detail=ENTITY_NOT_FOUND)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Failed to delete encounter {encounter_id} for user {user_id}, world {world_id}: {e}"
        )
        raise HTTPException(status_code=500, detail=INTERNAL_SERVER_ERROR)


@router.post("/connections", response_model=Connection, status_code=201)
async def create_connection(
    connection_data: ConnectionCreate,
    session: UserSession = Depends(validate_current_user_world),
    db_session: AsyncSession = Depends(get_async_db_routes_session),
):
    """Create a new connection between encounters"""
    user_id, world_id = session.user_id, session.world_id
    try:
        encounter_store = EncounterStore(
            user_id=user_id, world_id=world_id, session=session
        )
        connection_store = ConnectionStore(
            user_id=user_id, world_id=world_id, session=db_session
        )

        # Validate that both encounters exist
        if not await encounter_store.get_by_id(connection_data.source_encounter_id):
            raise HTTPException(status_code=404, detail=ENTITY_NOT_FOUND)
        if not await encounter_store.get_by_id(connection_data.target_encounter_id):
            raise HTTPException(status_code=404, detail=ENTITY_NOT_FOUND)

        return await connection_store.create(connection_data)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Failed to create connection for user {user_id}, world {world_id}: {e}"
        )
        raise HTTPException(status_code=500, detail=INTERNAL_SERVER_ERROR)


@router.put("/connections/{connection_id}", response_model=Connection)
async def update_connection(
    connection_id: int,
    connection_update: ConnectionUpdate,
    session: UserSession = Depends(validate_current_user_world),
    db_session: AsyncSession = Depends(get_async_db_routes_session),
):
    """Update an existing connection"""
    user_id, world_id = session.user_id, session.world_id
    try:
        encounter_store = EncounterStore(
            user_id=user_id, world_id=world_id, session=session
        )
        connection_store = ConnectionStore(
            user_id=user_id, world_id=world_id, session=db_session
        )

        # Override the ID from the URL path
        connection_update.id = connection_id

        # If updating encounter IDs, validate they exist
        if connection_update.source_encounter_id is not None:
            if not await encounter_store.get_by_id(
                connection_update.source_encounter_id
            ):
                raise HTTPException(status_code=404, detail=ENTITY_NOT_FOUND)
        if connection_update.target_encounter_id is not None:
            if not await encounter_store.get_by_id(
                connection_update.target_encounter_id
            ):
                raise HTTPException(status_code=404, detail=ENTITY_NOT_FOUND)

        connection = await connection_store.update(connection_id, connection_update)
        if not connection:
            raise HTTPException(status_code=404, detail=ENTITY_NOT_FOUND)
        return connection
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Failed to update connection {connection_id} for user {user_id}, world {world_id}: {e}"
        )
        raise HTTPException(status_code=500, detail=INTERNAL_SERVER_ERROR)


@router.delete("/connections/{connection_id}", status_code=204)
async def delete_connection(
    connection_id: int,
    session: UserSession = Depends(validate_current_user_world),
):
    """Delete a connection"""
    user_id, world_id = session.user_id, session.world_id
    try:
        success = await ConnectionStore(user_id=user_id, world_id=world_id).delete(
            connection_id
        )
        if not success:
            raise HTTPException(status_code=404, detail=ENTITY_NOT_FOUND)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Failed to delete connection {connection_id} for user {user_id}, world {world_id}: {e}"
        )
        raise HTTPException(status_code=500, detail=INTERNAL_SERVER_ERROR)


@router.get("/{encounter_id}/connections", response_model=List[Connection])
async def get_encounter_connections(
    encounter_id: int,
    session: UserSession = Depends(validate_current_user_world),
    db_session: AsyncSession = Depends(get_async_db_routes_session),
):
    """Get all connections for a specific encounter"""
    user_id, world_id = session.user_id, session.world_id
    try:
        encounter_store = EncounterStore(
            user_id=user_id, world_id=world_id, session=session
        )
        connection_store = ConnectionStore(
            user_id=user_id, world_id=world_id, session=db_session
        )

        # Validate encounter exists
        if not await encounter_store.get_by_id(encounter_id):
            raise HTTPException(status_code=404, detail=ENTITY_NOT_FOUND)

        return await connection_store.get_connections_for_encounter(encounter_id)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Failed to get connections for encounter {encounter_id}, user {user_id}, world {world_id}: {e}"
        )
        raise HTTPException(status_code=500, detail=INTERNAL_SERVER_ERROR)


@router.get(
    "/{encounter_id}/conversation/{player_id}/{character_id}",
    response_model=ConversationData,
)
async def get_conversation_data(
    encounter_id: int,
    player_id: int,
    character_id: int,
    session: UserSession = Depends(validate_current_user_world),
) -> Dict:
    """Get current influence and reveals data for a player/character combination"""
    user_id, world_id = session.user_id, session.world_id

    try:
        ctx = await get_conversation_context(
            world_id=world_id,
            player_id=player_id,
            user_id=user_id,
            character_id=character_id,
            encounter_id=encounter_id,
        )

        return ConversationData(
            influence=ctx.influence.score,
            reveals=[
                calculate_reveal_progress(reveal, ctx.influence.score)
                for reveal in ctx.reveals
            ],
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Failed to get conversation data for player {player_id}, encounter {encounter_id} and character {character_id}: {e}"
        )
        raise HTTPException(status_code=500, detail=INTERNAL_SERVER_ERROR)


@router.websocket("/{encounter_id}/conversation/{player_id}/{character_id}")
@observe
async def websocket_convo_endpoint(
    websocket: WebSocket,
    encounter_id: int,
    player_id: int,
    character_id: int,
):
    # Get context
    session = await get_websocket_user_world(websocket)
    user_id, world_id = session.user_id, session.world_id
    player_initiated = (
        websocket.query_params.get("player_init", "false").lower() == "true"
    )

    # Update trace
    get_client().update_current_trace(
        user_id=user_id,
        tags=["conversation"],
        metadata={
            "service": get_or_throw("SERVICE"),
            "env": get_or_throw("ENVIRONMENT"),
            "player_initiated": player_initiated,
        },
    )

    return await have_conversation(
        websocket=websocket,
        world_id=world_id,
        user_id=user_id,
        encounter_id=encounter_id,
        player_id=player_id,
        character_id=character_id,
        player_initiated=player_initiated,
    )


@router.websocket("/{encounter_id}/challenge/{player_id}/{character_id}")
@observe
async def websocket_challenge_endpoint(
    websocket: WebSocket,
    encounter_id: int,
    player_id: int,
    character_id: int,
):
    # Get context
    session = await get_websocket_user_world(websocket)
    user_id, world_id = session.user_id, session.world_id
    skill = websocket.query_params.get("skill")
    d20_roll = websocket.query_params.get("d20_roll")
    player_initiated = (
        websocket.query_params.get("player_init", "false").lower() == "true"
    )

    # Update trace
    get_client().update_current_trace(
        user_id=user_id,
        tags=["challenge"],
        metadata={
            "service": get_or_throw("SERVICE"),
            "env": get_or_throw("ENVIRONMENT"),
            "player_initiated": player_initiated,
        },
    )

    return await challenge_character(
        websocket=websocket,
        world_id=world_id,
        user_id=user_id,
        encounter_id=encounter_id,
        player_id=player_id,
        character_id=character_id,
        skill=skill,
        d20_roll=int(d20_roll),
        player_initiated=player_initiated,
    )
