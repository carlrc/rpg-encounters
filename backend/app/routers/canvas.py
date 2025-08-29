import logging

from fastapi import APIRouter, Depends, HTTPException

from app.data.connection_store import ConnectionStore
from app.data.encounter_store import EncounterStore
from app.db.connection import get_db_session
from app.dependencies import get_current_user_world
from app.http import ENTITY_NOT_FOUND, INTERNAL_SERVER_ERROR
from app.models.canvas import CanvasResponse, CanvasSaveRequest
from app.models.encounter import EncounterCreate, EncounterUpdate

router = APIRouter(prefix="/api/canvas", tags=["canvas"])

logger = logging.getLogger(__name__)


@router.get("", response_model=CanvasResponse)
async def get_canvas(user_world: tuple[int, int] = Depends(get_current_user_world)):
    """Get complete canvas state - all encounters with connections"""
    user_id, world_id = user_world
    try:
        with get_db_session() as session:
            encounter_store = EncounterStore(
                user_id=user_id, world_id=world_id, session=session
            )
            connection_store = ConnectionStore(
                user_id=user_id, world_id=world_id, session=session
            )

            encounters = encounter_store.get_all_encounters()
            connections = connection_store.get_all_connections()

            return CanvasResponse(encounters=encounters, connections=connections)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get canvas for user {user_id}, world {world_id}: {e}")
        raise HTTPException(status_code=500, detail=INTERNAL_SERVER_ERROR)


@router.post("", response_model=CanvasResponse)
async def save_canvas(
    request: CanvasSaveRequest,
    user_world: tuple[int, int] = Depends(get_current_user_world),
):
    """Save entire canvas state - handles new, existing, and deleted items"""
    user_id, world_id = user_world
    try:
        with get_db_session() as session:
            encounter_store = EncounterStore(
                user_id=user_id, world_id=world_id, session=session
            )
            connection_store = ConnectionStore(
                user_id=user_id, world_id=world_id, session=session
            )

            # Delete encounters and their connections
            for encounter_id in request.deleted_encounter_ids:
                # Delete all connections referencing this encounter
                connections = connection_store.get_connections_for_encounter(
                    encounter_id
                )
                for connection in connections:
                    connection_store.delete_connection(connection.id)

                # Delete the encounter itself
                encounter_store.delete_encounter(encounter_id)

            # Delete additional connections (manually deleted by user)
            for connection_id in request.deleted_connection_ids:
                connection_store.delete_connection(connection_id)

            # Build encounter ID mapping dictionary (temp_id -> real_id)
            encounter_id_map = {}

            # Collect all encounters and connections for response
            all_encounters = []
            all_connections = []

            # Create new encounters (translate temp IDs to real IDs)
            for encounter_data in request.new_encounters:
                # Store temp ID before creating encounter
                temp_id = encounter_data.id

                # Create EncounterCreate object without the temp ID
                encounter_create = EncounterCreate(
                    **encounter_data.model_dump(exclude={"id"})
                )

                created = encounter_store.create_encounter(encounter_create)
                all_encounters.append(created)
                # Map temp ID to real database ID
                encounter_id_map[temp_id] = created.id

            # Update existing encounters
            for encounter_update in request.existing_encounters:
                if not encounter_update.id:
                    raise HTTPException(
                        status_code=400, detail="Existing encounter missing ID"
                    )
                updated = encounter_store.update_encounter(
                    encounter_id=int(encounter_update.id),
                    encounter_update=EncounterUpdate(
                        **encounter_update.model_dump(exclude={"id"})
                    ),
                )
                if not updated:
                    raise HTTPException(status_code=404, detail=ENTITY_NOT_FOUND)
                all_encounters.append(updated)
                # Add existing encounters to map (they keep their real IDs)
                encounter_id_map[encounter_update.id] = updated.id

            # Create new connections (translate temp IDs to real IDs)
            for connection_data in request.new_connections:
                # Translate source encounter ID using the mapping
                source_id = encounter_id_map.get(connection_data.source_encounter_id)
                if source_id is None:
                    # If not in map, it might be an existing encounter - check database
                    existing_encounter = encounter_store.get_encounter_by_id(
                        connection_data.source_encounter_id
                    )

                    if not existing_encounter:
                        logger.error(
                            f"Source encounter {connection_data.source_encounter_id} not found"
                        )
                        raise HTTPException(status_code=404, detail=ENTITY_NOT_FOUND)

                    source_id = existing_encounter.id
                    encounter_id_map[source_id] = (
                        source_id  # Add to map for future lookups
                    )

                # Translate target encounter ID using the mapping
                target_id = encounter_id_map.get(connection_data.target_encounter_id)
                if target_id is None:
                    # If not in map, it might be an existing encounter - check database
                    existing_encounter = encounter_store.get_encounter_by_id(
                        connection_data.target_encounter_id
                    )

                    if not existing_encounter:
                        logger.error(
                            f"Target encounter {connection_data.source_encounter_id} not found"
                        )
                        raise HTTPException(status_code=404, detail=ENTITY_NOT_FOUND)

                    target_id = existing_encounter.id
                    encounter_id_map[target_id] = (
                        target_id  # Add to map for future lookups
                    )

                # Update the connection data with real IDs
                connection_data.source_encounter_id = source_id
                connection_data.target_encounter_id = target_id

                created = connection_store.create_connection(connection_data)
                all_connections.append(created)

            # Update existing connections
            for connection_update in request.existing_connections:
                if not connection_update.id:
                    raise HTTPException(
                        status_code=400, detail="Existing connection missing ID"
                    )
                updated = connection_store.update_connection(
                    connection_update.id, connection_update
                )
                if not updated:
                    raise HTTPException(status_code=404, detail=ENTITY_NOT_FOUND)
                all_connections.append(updated)

            return CanvasResponse(
                encounters=all_encounters, connections=all_connections
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to save canvas for user {user_id}, world {world_id}: {e}")
        raise HTTPException(status_code=500, detail=INTERNAL_SERVER_ERROR)
