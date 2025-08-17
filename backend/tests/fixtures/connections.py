from app.models.encounter_connection import Connection, EdgeType, ConnectionHandle

connections_db = {
    1: Connection(
        id=1,
        source_encounter_id=1,  # Tavern
        target_encounter_id=2,  # Village Square
        source_handle=ConnectionHandle.RIGHT.value,
        target_handle=ConnectionHandle.LEFT.value,
        edge_type=EdgeType.STRAIGHT.value,
        stroke_color="#007bff",
        stroke_width=3
    ),
    2: Connection(
        id=2,
        source_encounter_id=2,  # Village Square
        target_encounter_id=3,  # Community Gardens
        source_handle=ConnectionHandle.BOTTOM.value,
        target_handle=ConnectionHandle.TOP.value,
        edge_type=EdgeType.SMOOTH_STEP.value,
        stroke_color="#28a745",
        stroke_width=2
    ),
    3: Connection(
        id=3,
        source_encounter_id=2,  # Village Square
        target_encounter_id=4,  # Forest Path
        source_handle=ConnectionHandle.RIGHT.value,
        target_handle=ConnectionHandle.LEFT.value,
        edge_type=EdgeType.BEZIER.value,
        stroke_color="#6c757d",
        stroke_width=3
    )
}

next_connection_id = 4