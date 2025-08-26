from typing import Dict, List

from fastapi import APIRouter, Depends, HTTPException, WebSocket

from app.data.connection_store import ConnectionStore
from app.data.encounter_store import EncounterStore
from app.dependencies import get_current_user_world
from app.models.batch_update import (
    BatchCreateConnectionsRequest,
    BatchCreateEncountersRequest,
    BatchDeleteConnectionsRequest,
    BatchDeleteEncountersRequest,
    BatchUpdateConnectionsRequest,
    BatchUpdateEncountersRequest,
)
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

router = APIRouter(prefix="/api/encounters", tags=["encounters"])


@router.get("/")
async def get_encounters(user_world: tuple[int, int] = Depends(get_current_user_world)):
    """Get all encounters with connections - returns the complete canvas state"""
    user_id, world_id = user_world
    encounters = EncounterStore(user_id=user_id, world_id=world_id).get_all_encounters()
    connections = ConnectionStore(
        user_id=user_id, world_id=world_id
    ).get_all_connections()

    return {"encounters": encounters, "connections": connections}


@router.get("/{encounter_id}", response_model=Encounter)
async def get_encounter(
    encounter_id: int, user_world: tuple[int, int] = Depends(get_current_user_world)
):
    """Get a specific encounter by ID"""
    user_id, world_id = user_world
    encounter = EncounterStore(user_id=user_id, world_id=world_id).get_encounter_by_id(
        encounter_id
    )
    if not encounter:
        raise HTTPException(status_code=404, detail="Encounter not found")
    return encounter


@router.post("/", response_model=Encounter, status_code=201)
async def create_encounter(
    encounter_data: EncounterCreate,
    user_world: tuple[int, int] = Depends(get_current_user_world),
):
    """Create a new encounter"""
    user_id, world_id = user_world
    return EncounterStore(user_id=user_id, world_id=world_id).create_encounter(
        encounter_data
    )


@router.put("/{encounter_id}", response_model=Encounter)
async def update_encounter(
    encounter_id: int,
    encounter_update: EncounterUpdate,
    user_world: tuple[int, int] = Depends(get_current_user_world),
):
    """Update an existing encounter"""
    user_id, world_id = user_world
    # Override the ID from the URL path
    encounter_update.id = encounter_id
    encounter = EncounterStore(user_id=user_id, world_id=world_id).update_encounter(
        encounter_id, encounter_update
    )
    if not encounter:
        raise HTTPException(status_code=404, detail="Encounter not found")
    return encounter


@router.delete("/{encounter_id}", status_code=204)
async def delete_encounter(
    encounter_id: int, user_world: tuple[int, int] = Depends(get_current_user_world)
):
    """Delete an encounter"""
    user_id, world_id = user_world
    success = EncounterStore(user_id=user_id, world_id=world_id).delete_encounter(
        encounter_id
    )
    if not success:
        raise HTTPException(status_code=404, detail="Encounter not found")
    return None


@router.post("/connections", response_model=Connection, status_code=201)
async def create_connection(
    connection_data: ConnectionCreate,
    user_world: tuple[int, int] = Depends(get_current_user_world),
):
    """Create a new connection between encounters"""
    user_id, world_id = user_world
    # Validate that both encounters exist
    encounter_store = EncounterStore(user_id=user_id, world_id=world_id)
    if not encounter_store.get_encounter_by_id(connection_data.source_encounter_id):
        raise HTTPException(status_code=404, detail="Source encounter not found")
    if not encounter_store.get_encounter_by_id(connection_data.target_encounter_id):
        raise HTTPException(status_code=404, detail="Target encounter not found")

    return ConnectionStore(user_id=user_id, world_id=world_id).create_connection(
        connection_data
    )


@router.put("/connections/{connection_id}", response_model=Connection)
async def update_connection(
    connection_id: int,
    connection_update: ConnectionUpdate,
    user_world: tuple[int, int] = Depends(get_current_user_world),
):
    """Update an existing connection"""
    user_id, world_id = user_world
    # Override the ID from the URL path
    connection_update.id = connection_id

    encounter_store = EncounterStore(user_id=user_id, world_id=world_id)
    # If updating encounter IDs, validate they exist
    if connection_update.source_encounter_id is not None:
        if not encounter_store.get_encounter_by_id(
            connection_update.source_encounter_id
        ):
            raise HTTPException(status_code=404, detail="Source encounter not found")
    if connection_update.target_encounter_id is not None:
        if not encounter_store.get_encounter_by_id(
            connection_update.target_encounter_id
        ):
            raise HTTPException(status_code=404, detail="Target encounter not found")

    connection = ConnectionStore(user_id=user_id, world_id=world_id).update_connection(
        connection_id, connection_update
    )
    if not connection:
        raise HTTPException(status_code=404, detail="Connection not found")
    return connection


@router.delete("/connections/{connection_id}", status_code=204)
async def delete_connection(
    connection_id: int, user_world: tuple[int, int] = Depends(get_current_user_world)
):
    """Delete a connection"""
    user_id, world_id = user_world
    success = ConnectionStore(user_id=user_id, world_id=world_id).delete_connection(
        connection_id
    )
    if not success:
        raise HTTPException(status_code=404, detail="Connection not found")
    return None


@router.get("/{encounter_id}/connections", response_model=List[Connection])
async def get_encounter_connections(
    encounter_id: int, user_world: tuple[int, int] = Depends(get_current_user_world)
):
    """Get all connections for a specific encounter"""
    user_id, world_id = user_world
    # Validate encounter exists
    if not EncounterStore(user_id=user_id, world_id=world_id).get_encounter_by_id(
        encounter_id
    ):
        raise HTTPException(status_code=404, detail="Encounter not found")

    return ConnectionStore(
        user_id=user_id, world_id=world_id
    ).get_connections_for_encounter(encounter_id)


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
        # TODO: Wasted db calls to influence, memories and messages
        context = get_conversation_context(
            world_id=world_id,
            player_id=player_id,
            user_id=user_id,
            character_id=character_id,
            encounter_id=encounter_id,
            base_influence=0,
        )

        # Format response to match WebSocket conversation_data format
        return {
            "type": "conversation_data",
            "influence": context.influence.score,
            "reveals": [
                calculate_reveal_progress(reveal, context.influence.score)
                for reveal in context.reveals
            ],
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get conversation data: {str(e)}"
        )


# Batch endpoints
@router.post("/batch/create", response_model=List[Encounter], status_code=201)
async def batch_create_encounters(
    request: BatchCreateEncountersRequest,
    user_world: tuple[int, int] = Depends(get_current_user_world),
):
    """Create multiple encounters in a single request"""
    user_id, world_id = user_world
    created_encounters = []

    encounter_store = EncounterStore(user_id=user_id, world_id=world_id)
    for encounter_data in request.encounters:
        created_encounter = encounter_store.create_encounter(encounter_data)
        created_encounters.append(created_encounter)

    return created_encounters


@router.put("/batch/update", response_model=List[Encounter])
async def batch_update_encounters(
    request: BatchUpdateEncountersRequest,
    user_world: tuple[int, int] = Depends(get_current_user_world),
):
    """Update multiple encounters in a single request"""
    user_id, world_id = user_world
    updated_encounters = []

    encounter_store = EncounterStore(user_id=user_id, world_id=world_id)
    for encounter_update in request.encounters:
        updated_encounter = encounter_store.update_encounter(
            encounter_update.id, encounter_update
        )
        if not updated_encounter:
            raise HTTPException(
                status_code=404,
                detail=f"Encounter with id {encounter_update.id} not found",
            )
        updated_encounters.append(updated_encounter)

    return updated_encounters


@router.delete("/batch/delete", status_code=204)
async def batch_delete_encounters(
    request: BatchDeleteEncountersRequest,
    user_world: tuple[int, int] = Depends(get_current_user_world),
):
    """Delete multiple encounters in a single request"""
    user_id, world_id = user_world
    encounter_store = EncounterStore(user_id=user_id, world_id=world_id)
    for encounter_id in request.encounter_ids:
        success = encounter_store.delete_encounter(encounter_id)
        if not success:
            raise HTTPException(
                status_code=404, detail=f"Encounter with id {encounter_id} not found"
            )

    return None


@router.post(
    "/connections/batch/create", response_model=List[Connection], status_code=201
)
async def batch_create_connections(
    request: BatchCreateConnectionsRequest,
    user_world: tuple[int, int] = Depends(get_current_user_world),
):
    """Create multiple connections in a single request"""
    user_id, world_id = user_world
    encounter_store = EncounterStore(user_id=user_id, world_id=world_id)
    connection_store = ConnectionStore(user_id=user_id, world_id=world_id)
    created_connections = []

    for connection_data in request.connections:
        # Validate that both encounters exist
        if not encounter_store.get_encounter_by_id(connection_data.source_encounter_id):
            raise HTTPException(
                status_code=404,
                detail=f"Source encounter {connection_data.source_encounter_id} not found",
            )
        if not encounter_store.get_encounter_by_id(connection_data.target_encounter_id):
            raise HTTPException(
                status_code=404,
                detail=f"Target encounter {connection_data.target_encounter_id} not found",
            )

        created_connection = connection_store.create_connection(connection_data)
        created_connections.append(created_connection)

    return created_connections


@router.put("/connections/batch/update", response_model=List[Connection])
async def batch_update_connections(
    request: BatchUpdateConnectionsRequest,
    user_world: tuple[int, int] = Depends(get_current_user_world),
):
    """Update multiple connections in a single request"""
    user_id, world_id = user_world
    encounter_store = EncounterStore(user_id=user_id, world_id=world_id)
    connection_store = ConnectionStore(user_id=user_id, world_id=world_id)
    updated_connections = []

    for connection_update in request.connections:
        # Validate encounter references if they're being updated
        if connection_update.source_encounter_id is not None:
            if not encounter_store.get_encounter_by_id(
                connection_update.source_encounter_id
            ):
                raise HTTPException(
                    status_code=404,
                    detail=f"Source encounter {connection_update.source_encounter_id} not found",
                )
        if connection_update.target_encounter_id is not None:
            if not encounter_store.get_encounter_by_id(
                connection_update.target_encounter_id
            ):
                raise HTTPException(
                    status_code=404,
                    detail=f"Target encounter {connection_update.target_encounter_id} not found",
                )

        updated_connection = connection_store.update_connection(
            connection_update.id, connection_update
        )
        if not updated_connection:
            raise HTTPException(
                status_code=404,
                detail=f"Connection with id {connection_update.id} not found",
            )
        updated_connections.append(updated_connection)

    return updated_connections


@router.delete("/connections/batch/delete", status_code=204)
async def batch_delete_connections(
    request: BatchDeleteConnectionsRequest,
    user_world: tuple[int, int] = Depends(get_current_user_world),
):
    """Delete multiple connections in a single request"""
    user_id, world_id = user_world
    connection_store = ConnectionStore(user_id=user_id, world_id=world_id)
    for connection_id in request.connection_ids:
        success = connection_store.delete_connection(connection_id)
        if not success:
            raise HTTPException(
                status_code=404, detail=f"Connection with id {connection_id} not found"
            )

    return None


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
