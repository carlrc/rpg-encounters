import logging
from typing import Dict, List

from fastapi import APIRouter, Depends, HTTPException, WebSocket

from app.data.character_store import CharacterStore
from app.data.connection_store import ConnectionStore
from app.data.encounter_store import EncounterStore
from app.data.player_store import PlayerStore
from app.db.connection import get_db_session
from app.dependencies import get_current_user_world
from app.models.encounter import Encounter, EncounterCreate, EncounterUpdate
from app.models.encounter_connection import (
    Connection,
    ConnectionCreate,
    ConnectionUpdate,
)
from app.services.challenge import challenge_character
from app.services.context import get_conversation_context
from app.services.conversation import have_conversation
from app.services.influence_calculator import calculate_base_influence
from app.services.reveal_progress import calculate_reveal_progress

router = APIRouter(prefix="/api/encounters", tags=["encounters"])

logger = logging.getLogger(__name__)


@router.get("/{encounter_id}", response_model=Encounter)
async def get_encounter(
    encounter_id: int,
    user_world: tuple[int, int] = Depends(get_current_user_world),
):
    """Get a specific encounter by ID"""
    user_id, world_id = user_world
    try:
        encounter = EncounterStore(
            user_id=user_id, world_id=world_id
        ).get_encounter_by_id(encounter_id)
        if not encounter:
            raise HTTPException(status_code=404, detail="Encounter not found")
        return encounter
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Failed to get encounter {encounter_id} for user {user_id}, world {world_id}: {e}"
        )
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.post("/", response_model=Encounter, status_code=201)
async def create_encounter(
    encounter_data: EncounterCreate,
    user_world: tuple[int, int] = Depends(get_current_user_world),
):
    """Create a new encounter"""
    user_id, world_id = user_world
    try:
        return EncounterStore(user_id=user_id, world_id=world_id).create_encounter(
            encounter_data
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Failed to create encounter for user {user_id}, world {world_id}: {e}"
        )
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.put("/{encounter_id}", response_model=Encounter)
async def update_encounter(
    encounter_id: int,
    encounter_update: EncounterUpdate,
    user_world: tuple[int, int] = Depends(get_current_user_world),
):
    """Update an existing encounter"""
    user_id, world_id = user_world
    try:
        # Override the ID from the URL path
        encounter_update.id = encounter_id
        encounter = EncounterStore(user_id=user_id, world_id=world_id).update_encounter(
            encounter_id, encounter_update
        )
        if not encounter:
            raise HTTPException(status_code=404, detail="Encounter not found")
        return encounter
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Failed to update encounter {encounter_id} for user {user_id}, world {world_id}: {e}"
        )
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.delete("/{encounter_id}", status_code=204)
async def delete_encounter(
    encounter_id: int,
    user_world: tuple[int, int] = Depends(get_current_user_world),
):
    """Delete an encounter"""
    user_id, world_id = user_world
    try:
        success = EncounterStore(user_id=user_id, world_id=world_id).delete_encounter(
            encounter_id
        )
        if not success:
            raise HTTPException(status_code=404, detail="Encounter not found")
        return None
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Failed to delete encounter {encounter_id} for user {user_id}, world {world_id}: {e}"
        )
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.post("/connections", response_model=Connection, status_code=201)
async def create_connection(
    connection_data: ConnectionCreate,
    user_world: tuple[int, int] = Depends(get_current_user_world),
):
    """Create a new connection between encounters"""
    user_id, world_id = user_world
    try:
        with get_db_session() as session:
            encounter_store = EncounterStore(
                user_id=user_id, world_id=world_id, session=session
            )
            connection_store = ConnectionStore(
                user_id=user_id, world_id=world_id, session=session
            )

            # Validate that both encounters exist
            if not encounter_store.get_encounter_by_id(
                connection_data.source_encounter_id
            ):
                raise HTTPException(
                    status_code=404, detail="Source encounter not found"
                )
            if not encounter_store.get_encounter_by_id(
                connection_data.target_encounter_id
            ):
                raise HTTPException(
                    status_code=404, detail="Target encounter not found"
                )

            return connection_store.create_connection(connection_data)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Failed to create connection for user {user_id}, world {world_id}: {e}"
        )
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.put("/connections/{connection_id}", response_model=Connection)
async def update_connection(
    connection_id: int,
    connection_update: ConnectionUpdate,
    user_world: tuple[int, int] = Depends(get_current_user_world),
):
    """Update an existing connection"""
    user_id, world_id = user_world
    try:
        with get_db_session() as session:
            encounter_store = EncounterStore(
                user_id=user_id, world_id=world_id, session=session
            )
            connection_store = ConnectionStore(
                user_id=user_id, world_id=world_id, session=session
            )

            # Override the ID from the URL path
            connection_update.id = connection_id

            # If updating encounter IDs, validate they exist
            if connection_update.source_encounter_id is not None:
                if not encounter_store.get_encounter_by_id(
                    connection_update.source_encounter_id
                ):
                    raise HTTPException(
                        status_code=404, detail="Source encounter not found"
                    )
            if connection_update.target_encounter_id is not None:
                if not encounter_store.get_encounter_by_id(
                    connection_update.target_encounter_id
                ):
                    raise HTTPException(
                        status_code=404, detail="Target encounter not found"
                    )

            connection = connection_store.update_connection(
                connection_id, connection_update
            )
            if not connection:
                raise HTTPException(status_code=404, detail="Connection not found")
            return connection
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Failed to update connection {connection_id} for user {user_id}, world {world_id}: {e}"
        )
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.delete("/connections/{connection_id}", status_code=204)
async def delete_connection(
    connection_id: int,
    user_world: tuple[int, int] = Depends(get_current_user_world),
):
    """Delete a connection"""
    user_id, world_id = user_world
    try:
        success = ConnectionStore(user_id=user_id, world_id=world_id).delete_connection(
            connection_id
        )
        if not success:
            raise HTTPException(status_code=404, detail="Connection not found")
        return None
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Failed to delete connection {connection_id} for user {user_id}, world {world_id}: {e}"
        )
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get("/{encounter_id}/connections", response_model=List[Connection])
async def get_encounter_connections(
    encounter_id: int, user_world: tuple[int, int] = Depends(get_current_user_world)
):
    """Get all connections for a specific encounter"""
    user_id, world_id = user_world
    try:
        with get_db_session() as session:
            encounter_store = EncounterStore(
                user_id=user_id, world_id=world_id, session=session
            )
            connection_store = ConnectionStore(
                user_id=user_id, world_id=world_id, session=session
            )

            # Validate encounter exists
            if not encounter_store.get_encounter_by_id(encounter_id):
                raise HTTPException(status_code=404, detail="Not Found")

            return connection_store.get_connections_for_encounter(encounter_id)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Failed to get connections for encounter {encounter_id}, user {user_id}, world {world_id}: {e}"
        )
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get("/{encounter_id}/conversation/{player_id}/{character_id}")
async def get_conversation_data(
    encounter_id: int,
    player_id: int,
    character_id: int,
    user_world: tuple[int, int] = Depends(get_current_user_world),
) -> Dict:
    """Get current influence and reveals data for a player/character combination"""
    user_id, world_id = user_world

    try:
        with get_db_session() as session:
            character = CharacterStore(
                user_id=user_id, world_id=world_id, session=session
            ).get_character_by_id(character_id=character_id)
            player = PlayerStore(
                user_id=user_id, world_id=world_id, session=session
            ).get_player_by_id(player_id=player_id)

            if not character or not player:
                raise HTTPException(status_code=404, detail="Not found")

            base_influence = calculate_base_influence(
                character=character, player=player
            )
            context = get_conversation_context(
                world_id=world_id,
                player_id=player_id,
                user_id=user_id,
                character_id=character_id,
                encounter_id=encounter_id,
                base_influence=base_influence,
                session=session,
            )

        # TODO: Should be response class
        # Format response to match WebSocket conversation_data format
        return {
            "type": "conversation_data",
            "influence": context.influence.score,
            "reveals": [
                calculate_reveal_progress(reveal, context.influence.score)
                for reveal in context.reveals
            ],
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Failed to get conversation data for player {player_id}, encounter {encounter_id} and character {character_id}: {e}"
        )
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.websocket("/{encounter_id}/conversation/{player_id}/{character_id}")
async def websocket_convo_endpoint(
    websocket: WebSocket,
    encounter_id: int,
    player_id: int,
    character_id: int,
    user_world: tuple[int, int] = Depends(get_current_user_world),
):
    user_id, world_id = user_world
    return await have_conversation(
        websocket=websocket,
        world_id=world_id,
        user_id=user_id,
        encounter_id=encounter_id,
        player_id=player_id,
        character_id=character_id,
    )


@router.websocket("/{encounter_id}/challenge/{player_id}/{character_id}")
async def websocket_challenge_endpoint(
    websocket: WebSocket,
    encounter_id: int,
    player_id: int,
    character_id: int,
    user_world: tuple[int, int] = Depends(get_current_user_world),
):
    user_id, world_id = user_world
    skill = websocket.query_params.get("skill")
    d20_roll = websocket.query_params.get("d20_roll")
    return await challenge_character(
        websocket=websocket,
        world_id=world_id,
        user_id=user_id,
        encounter_id=encounter_id,
        player_id=player_id,
        character_id=character_id,
        skill=skill,
        d20_roll=int(d20_roll),
    )
