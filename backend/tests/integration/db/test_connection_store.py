#!/usr/bin/env python3
import os

from sqlalchemy import create_engine

from app.data.connection_store import ConnectionStore
from app.data.encounter_store import EncounterStore
from app.models.encounter import EncounterCreate
from app.models.encounter_connection import (
    ConnectionCreate,
    ConnectionHandle,
    ConnectionUpdate,
    EdgeType,
)


def test_connection_store():
    url = os.getenv("TEST_DATABASE_URL")
    encounter_store = EncounterStore(user_id=1, world_id=1, engine=create_engine(url))

    encounter1_data = EncounterCreate(
        name="Test Tavern",
        description="A cozy tavern",
        position_x=100.0,
        position_y=200.0,
        character_ids=[],
    )

    encounter2_data = EncounterCreate(
        name="Test Village Square",
        description="The heart of the village",
        position_x=300.0,
        position_y=200.0,
        character_ids=[],
    )

    created_encounter1 = encounter_store.create_encounter(encounter1_data)
    created_encounter2 = encounter_store.create_encounter(encounter2_data)

    # Now create connection with actual encounter IDs
    connection_store = ConnectionStore(user_id=1, world_id=1, engine=create_engine(url))

    new_connection_data = ConnectionCreate(
        source_encounter_id=created_encounter1.id,
        target_encounter_id=created_encounter2.id,
        source_handle=ConnectionHandle.RIGHT.value,
        target_handle=ConnectionHandle.LEFT.value,
        edge_type=EdgeType.STRAIGHT.value,
        stroke_color="#007bff",
        stroke_width=3,
    )

    created_connection = connection_store.create_connection(new_connection_data)
    assert created_connection.source_encounter_id == created_encounter1.id
    assert created_connection.target_encounter_id == created_encounter2.id
    assert created_connection.id is not None

    all_connections = connection_store.get_all_connections()
    assert len(all_connections) == 1

    retrieved_connection = connection_store.get_connection_by_id(created_connection.id)
    assert retrieved_connection is not None

    encounter_connections = connection_store.get_connections_for_encounter(
        created_encounter1.id
    )
    assert len(encounter_connections) == 1

    update_data = ConnectionUpdate(
        stroke_color="#28a745",
        stroke_width=5,
        edge_type=EdgeType.BEZIER.value,
    )
    updated_connection = connection_store.update_connection(
        created_connection.id, update_data
    )
    assert updated_connection is not None
    assert updated_connection.stroke_color == update_data.stroke_color
    assert updated_connection.stroke_width == update_data.stroke_width
    assert updated_connection.edge_type == update_data.edge_type

    exists = connection_store.connection_exists(created_connection.id)
    assert exists is True

    deleted = connection_store.delete_connection(created_connection.id)
    assert deleted is True

    exists_after_delete = connection_store.connection_exists(created_connection.id)
    assert exists_after_delete is False
