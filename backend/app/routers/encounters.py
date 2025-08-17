from typing import List

from fastapi import APIRouter, HTTPException, WebSocket

from app.data.connection_store import ConnectionStore
from app.data.encounter_store import EncounterStore
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
from app.services.conversation import conversation

router = APIRouter(prefix="/api/encounters", tags=["encounters"])


@router.get("/")
async def get_encounters():
    """Get all encounters with connections - returns the complete canvas state"""
    encounters = EncounterStore().get_all_encounters()
    connections = ConnectionStore().get_all_connections()

    return {"encounters": encounters, "connections": connections}


@router.get("/{encounter_id}", response_model=Encounter)
async def get_encounter(encounter_id: int):
    """Get a specific encounter by ID"""
    encounter = EncounterStore().get_encounter_by_id(encounter_id)
    if not encounter:
        raise HTTPException(status_code=404, detail="Encounter not found")
    return encounter


@router.post("/", response_model=Encounter, status_code=201)
async def create_encounter(encounter_data: EncounterCreate):
    """Create a new encounter"""
    return EncounterStore().create_encounter(encounter_data)


@router.put("/{encounter_id}", response_model=Encounter)
async def update_encounter(encounter_id: int, encounter_update: EncounterUpdate):
    """Update an existing encounter"""
    # Override the ID from the URL path
    encounter_update.id = encounter_id
    encounter = EncounterStore().update_encounter(encounter_id, encounter_update)
    if not encounter:
        raise HTTPException(status_code=404, detail="Encounter not found")
    return encounter


@router.delete("/{encounter_id}", status_code=204)
async def delete_encounter(encounter_id: int):
    """Delete an encounter"""
    success = EncounterStore().delete_encounter(encounter_id)
    if not success:
        raise HTTPException(status_code=404, detail="Encounter not found")
    return None


@router.post("/connections", response_model=Connection, status_code=201)
async def create_connection(connection_data: ConnectionCreate):
    """Create a new connection between encounters"""
    # Validate that both encounters exist
    encounter_store = EncounterStore()
    if not encounter_store.get_encounter_by_id(connection_data.source_encounter_id):
        raise HTTPException(status_code=404, detail="Source encounter not found")
    if not encounter_store.get_encounter_by_id(connection_data.target_encounter_id):
        raise HTTPException(status_code=404, detail="Target encounter not found")

    return ConnectionStore().create_connection(connection_data)


@router.put("/connections/{connection_id}", response_model=Connection)
async def update_connection(connection_id: int, connection_update: ConnectionUpdate):
    """Update an existing connection"""
    # Override the ID from the URL path
    connection_update.id = connection_id

    encounter_store = EncounterStore()
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

    connection = ConnectionStore().update_connection(connection_id, connection_update)
    if not connection:
        raise HTTPException(status_code=404, detail="Connection not found")
    return connection


@router.delete("/connections/{connection_id}", status_code=204)
async def delete_connection(connection_id: int):
    """Delete a connection"""
    success = ConnectionStore().delete_connection(connection_id)
    if not success:
        raise HTTPException(status_code=404, detail="Connection not found")
    return None


@router.get("/{encounter_id}/connections", response_model=List[Connection])
async def get_encounter_connections(encounter_id: int):
    """Get all connections for a specific encounter"""
    # Validate encounter exists
    if not EncounterStore().get_encounter_by_id(encounter_id):
        raise HTTPException(status_code=404, detail="Encounter not found")

    return ConnectionStore().get_connections_for_encounter(encounter_id)


# Batch endpoints
@router.post("/batch/create", response_model=List[Encounter], status_code=201)
async def batch_create_encounters(request: BatchCreateEncountersRequest):
    """Create multiple encounters in a single request"""
    created_encounters = []

    for encounter_data in request.encounters:
        created_encounter = EncounterStore().create_encounter(encounter_data)
        created_encounters.append(created_encounter)

    return created_encounters


@router.put("/batch/update", response_model=List[Encounter])
async def batch_update_encounters(request: BatchUpdateEncountersRequest):
    """Update multiple encounters in a single request"""
    updated_encounters = []

    for encounter_update in request.encounters:
        updated_encounter = EncounterStore().update_encounter(
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
async def batch_delete_encounters(request: BatchDeleteEncountersRequest):
    """Delete multiple encounters in a single request"""
    for encounter_id in request.encounter_ids:
        success = EncounterStore().delete_encounter(encounter_id)
        if not success:
            raise HTTPException(
                status_code=404, detail=f"Encounter with id {encounter_id} not found"
            )

    return None


@router.post(
    "/connections/batch/create", response_model=List[Connection], status_code=201
)
async def batch_create_connections(request: BatchCreateConnectionsRequest):
    """Create multiple connections in a single request"""
    encounter_store = EncounterStore()
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

        created_connection = ConnectionStore().create_connection(connection_data)
        created_connections.append(created_connection)

    return created_connections


@router.put("/connections/batch/update", response_model=List[Connection])
async def batch_update_connections(request: BatchUpdateConnectionsRequest):
    """Update multiple connections in a single request"""
    encounter_store = EncounterStore()
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

        updated_connection = ConnectionStore().update_connection(
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
async def batch_delete_connections(request: BatchDeleteConnectionsRequest):
    """Delete multiple connections in a single request"""
    for connection_id in request.connection_ids:
        success = ConnectionStore().delete_connection(connection_id)
        if not success:
            raise HTTPException(
                status_code=404, detail=f"Connection with id {connection_id} not found"
            )

    return None


@router.websocket("/{encounter_id}/conversation/{player_id}/{character_id}")
async def websocket_endpoint(
    websocket: WebSocket, encounter_id: int, player_id: int, character_id: int
):
    return await conversation(
        websocket=websocket,
        encounter_id=encounter_id,
        player_id=player_id,
        character_id=character_id,
    )
