from fastapi import APIRouter, Depends, HTTPException

from app.data.connection_store import ConnectionStore
from app.data.encounter_store import EncounterStore
from app.dependencies import get_current_user_world
from app.models.batch_update import CanvasResponse, CanvasSaveRequest
from app.models.encounter import EncounterCreate, EncounterUpdate

router = APIRouter(prefix="/api/canvas", tags=["canvas"])


@router.get("", response_model=CanvasResponse)
async def get_canvas(user_world: tuple[int, int] = Depends(get_current_user_world)):
    """Get complete canvas state - all encounters with connections"""
    user_id, world_id = user_world
    encounters = EncounterStore(user_id=user_id, world_id=world_id).get_all_encounters()
    connections = ConnectionStore(
        user_id=user_id, world_id=world_id
    ).get_all_connections()

    return CanvasResponse(encounters=encounters, connections=connections)


@router.post("/save", response_model=CanvasResponse)
async def save_canvas(
    request: CanvasSaveRequest,
    user_world: tuple[int, int] = Depends(get_current_user_world),
):
    """Save entire canvas state - handles new and existing items"""
    user_id, world_id = user_world

    encounter_store = EncounterStore(user_id=user_id, world_id=world_id)
    connection_store = ConnectionStore(user_id=user_id, world_id=world_id)

    # Build encounter ID mapping dictionary (temp_id -> real_id)
    encounter_id_map = {}

    # Collect all encounters and connections for response
    all_encounters = []
    all_connections = []

    # 1. Create new encounters first (they get real IDs)
    for encounter_data in request.new_encounters:
        # Store temp ID before creating encounter
        temp_id = encounter_data.id

        # Create EncounterCreate object without the temp ID
        encounter_create = EncounterCreate(**encounter_data.model_dump(exclude={"id"}))

        created = encounter_store.create_encounter(encounter_create)
        all_encounters.append(created)
        # Map temp ID to real database ID
        encounter_id_map[temp_id] = created.id

    # 2. Update existing encounters
    for encounter_update in request.existing_encounters:
        if not encounter_update.id:
            raise HTTPException(status_code=400, detail="Existing encounter missing ID")
        updated = encounter_store.update_encounter(
            encounter_id=encounter_update.id,
            encounter_update=EncounterUpdate(
                **encounter_update.model_dump(exclude={"id"})
            ),
        )
        if not updated:
            raise HTTPException(
                status_code=404, detail=f"Encounter {encounter_update.id} not found"
            )
        all_encounters.append(updated)
        # Add existing encounters to map (they keep their real IDs)
        encounter_id_map[encounter_update.id] = updated.id

    # 3. Create new connections (translate temp IDs to real IDs)
    for connection_data in request.new_connections:
        # Translate source encounter ID using the mapping
        source_id = encounter_id_map.get(connection_data.source_encounter_id)
        if source_id is None:
            # If not in map, it might be an existing encounter - check database
            existing_encounter = encounter_store.get_encounter_by_id(
                connection_data.source_encounter_id
            )
            if existing_encounter:
                source_id = existing_encounter.id
                encounter_id_map[source_id] = source_id  # Add to map for future lookups
            else:
                raise HTTPException(
                    status_code=404, detail="Source encounter not found"
                )

        # Translate target encounter ID using the mapping
        target_id = encounter_id_map.get(connection_data.target_encounter_id)
        if target_id is None:
            # If not in map, it might be an existing encounter - check database
            existing_encounter = encounter_store.get_encounter_by_id(
                connection_data.target_encounter_id
            )
            if existing_encounter:
                target_id = existing_encounter.id
                encounter_id_map[target_id] = target_id  # Add to map for future lookups
            else:
                raise HTTPException(
                    status_code=404, detail="Target encounter not found"
                )

        # Update the connection data with real IDs
        connection_data.source_encounter_id = source_id
        connection_data.target_encounter_id = target_id

        created = connection_store.create_connection(connection_data)
        all_connections.append(created)

    # 4. Update existing connections
    for connection_update in request.existing_connections:
        if not connection_update.id:
            raise HTTPException(
                status_code=400, detail="Existing connection missing ID"
            )
        updated = connection_store.update_connection(
            connection_update.id, connection_update
        )
        if not updated:
            raise HTTPException(
                status_code=404, detail=f"Connection {connection_update.id} not found"
            )
        all_connections.append(updated)

    # Return the same structure as the encounters endpoint for easy reuse
    return CanvasResponse(encounters=all_encounters, connections=all_connections)
