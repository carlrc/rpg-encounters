from app.models.encounter_connection import ConnectionCreate, EdgeType, ConnectionHandle

connections_db = [
    ConnectionCreate(
        user_id=1,
        world_id=1,
        source_encounter_id=0,  # Tavern (array index)
        target_encounter_id=1,  # Village Square (array index)
        source_handle=ConnectionHandle.RIGHT.value,
        target_handle=ConnectionHandle.LEFT.value,
        edge_type=EdgeType.STRAIGHT.value,
        stroke_color="#007bff",
        stroke_width=3
    ),
    ConnectionCreate(
        user_id=1,
        world_id=1,
        source_encounter_id=1,  # Village Square (array index)
        target_encounter_id=2,  # Community Gardens (array index)
        source_handle=ConnectionHandle.BOTTOM.value,
        target_handle=ConnectionHandle.TOP.value,
        edge_type=EdgeType.SMOOTH_STEP.value,
        stroke_color="#28a745",
        stroke_width=2
    ),
    ConnectionCreate(
        user_id=1,
        world_id=1,
        source_encounter_id=1,  # Village Square (array index)
        target_encounter_id=3,  # Forest Path (array index)
        source_handle=ConnectionHandle.RIGHT.value,
        target_handle=ConnectionHandle.LEFT.value,
        edge_type=EdgeType.BEZIER.value,
        stroke_color="#6c757d",
        stroke_width=3
    )
]