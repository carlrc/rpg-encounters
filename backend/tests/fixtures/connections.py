from app.models.encounter_connection import ConnectionCreate, EdgeType, ConnectionHandle

connections_db = [
    # The Main Deck (index 1) connects to The Upper Deck (index 0) - going up
    ConnectionCreate(
        user_id=1,
        world_id=1,
        source_encounter_id=1,  # The Main Deck
        target_encounter_id=0,  # The Upper Deck
        source_handle=ConnectionHandle.TOP.value,
        target_handle=ConnectionHandle.BOTTOM.value,
        edge_type=EdgeType.STRAIGHT.value,
        stroke_color="#007bff",
        stroke_width=3
    ),
    # The Main Deck (index 1) connects to The Captain's Quarters (index 2) - same level
    ConnectionCreate(
        user_id=1,
        world_id=1,
        source_encounter_id=1,  # The Main Deck
        target_encounter_id=2,  # The Captain's Quarters
        source_handle=ConnectionHandle.RIGHT.value,
        target_handle=ConnectionHandle.LEFT.value,
        edge_type=EdgeType.STRAIGHT.value,
        stroke_color="#007bff",
        stroke_width=3
    ),
    # The Main Deck (index 1) connects to The Lower Deck (index 5) - going down
    ConnectionCreate(
        user_id=1,
        world_id=1,
        source_encounter_id=1,  # The Main Deck
        target_encounter_id=5,  # The Lower Deck
        source_handle=ConnectionHandle.BOTTOM.value,
        target_handle=ConnectionHandle.TOP.value,
        edge_type=EdgeType.STRAIGHT.value,
        stroke_color="#007bff",
        stroke_width=2
    ),
    # The Lower Deck (index 5) connects to The Hold (index 3) - going down
    ConnectionCreate(
        user_id=1,
        world_id=1,
        source_encounter_id=5,  # The Lower Deck
        target_encounter_id=3,  # The Hold
        source_handle=ConnectionHandle.BOTTOM.value,
        target_handle=ConnectionHandle.TOP.value,
        edge_type=EdgeType.STRAIGHT.value,
        stroke_color="#007bff",
        stroke_width=2
    ),
    # The Lower Deck (index 5) connects to The Crew Quarters (index 4) - same level
    ConnectionCreate(
        user_id=1,
        world_id=1,
        source_encounter_id=5,  # The Lower Deck
        target_encounter_id=4,  # The Crew Quarters
        source_handle=ConnectionHandle.RIGHT.value,
        target_handle=ConnectionHandle.LEFT.value,
        edge_type=EdgeType.STRAIGHT.value,
        stroke_color="#007bff",
        stroke_width=2
    )
]