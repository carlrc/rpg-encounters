from typing import List

from app.models.encounter_connection import (
    Connection,
    ConnectionCreate,
    ConnectionUpdate,
)
from tests.fixtures.connections import connections_db, next_connection_id


class ConnectionStore:
    def __init__(self):
        self.connections = connections_db
        self.next_id = next_connection_id

    def get_all_connections(self) -> List[Connection]:
        """Get all connections"""
        return list(self.connections.values())

    def get_connection_by_id(self, connection_id: int) -> Connection | None:
        """Get a specific connection by ID"""
        return self.connections.get(connection_id)

    def create_connection(self, connection_data: ConnectionCreate) -> Connection:
        """Create a new connection"""
        connection_dict = connection_data.model_dump()
        connection_dict["id"] = self.next_id

        new_connection = Connection(**connection_dict)
        self.connections[self.next_id] = new_connection
        self.next_id += 1

        return new_connection

    def update_connection(
        self, connection_id: int, connection_update: ConnectionUpdate
    ) -> Connection | None:
        """Update an existing connection"""
        if connection_id not in self.connections:
            return None

        existing_connection = self.connections[connection_id]
        update_data = connection_update.model_dump(exclude_unset=True)

        # Update the existing connection with new data
        updated_data = existing_connection.model_dump()
        updated_data.update(update_data)

        updated_connection = Connection(**updated_data)
        self.connections[connection_id] = updated_connection

        return updated_connection

    def delete_connection(self, connection_id: int) -> bool:
        """Delete a connection"""
        if connection_id not in self.connections:
            return False

        del self.connections[connection_id]
        return True

    def get_connections_for_encounter(self, encounter_id: int) -> List[Connection]:
        """Get all connections that involve a specific encounter"""
        return [
            conn
            for conn in self.connections.values()
            if conn.source_encounter_id == encounter_id
            or conn.target_encounter_id == encounter_id
        ]
