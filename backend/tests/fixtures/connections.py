from app.models.encounter_connection import Connection, EdgeType

connections_db = {
    1: Connection(
        id=1,
        source_encounter_id=1,  # Tavern
        target_encounter_id=2,  # Village Square
        source_handle="right",
        target_handle="left",
        edge_type=EdgeType.STRAIGHT,
        stroke_color="#007bff",
        stroke_width=3
    ),
    2: Connection(
        id=2,
        source_encounter_id=2,  # Village Square
        target_encounter_id=3,  # Community Gardens
        source_handle="bottom",
        target_handle="top",
        edge_type=EdgeType.SMOOTH_STEP,
        stroke_color="#28a745",
        stroke_width=2
    ),
    3: Connection(
        id=3,
        source_encounter_id=2,  # Village Square
        target_encounter_id=4,  # Forest Path
        source_handle="right",
        target_handle="left",
        edge_type=EdgeType.BEZIER,
        stroke_color="#6c757d",
        stroke_width=3
    )
}

next_connection_id = 4