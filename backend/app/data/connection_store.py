from typing import List

from sqlalchemy import Engine
from sqlalchemy.orm import sessionmaker

from app.db.connection import get_db_engine
from app.db.models.connection import ConnectionORM
from app.models.encounter_connection import (
    Connection,
    ConnectionCreate,
    ConnectionUpdate,
)


class ConnectionStore:
    def __init__(self, user_id: int, world_id: int, engine: Engine = get_db_engine()):
        self.Session = sessionmaker(engine)
        self.user_id = user_id
        self.world_id = world_id

    def get_all_connections(self) -> List[Connection]:
        """Get all connections for the current user and world"""
        with self.Session() as session:
            connection_orms = (
                session.query(ConnectionORM)
                .filter(
                    ConnectionORM.user_id == self.user_id,
                    ConnectionORM.world_id == self.world_id,
                )
                .all()
            )
            return [
                Connection.model_validate(connection_orm)
                for connection_orm in connection_orms
            ]

    def get_connection_by_id(self, connection_id: int) -> Connection | None:
        """Get a specific connection by ID for the current user and world"""
        with self.Session() as session:
            connection_orm = (
                session.query(ConnectionORM)
                .filter(
                    ConnectionORM.id == connection_id,
                    ConnectionORM.user_id == self.user_id,
                    ConnectionORM.world_id == self.world_id,
                )
                .first()
            )
            if connection_orm:
                return Connection.model_validate(connection_orm)
            return None

    def create_connection(self, connection_data: ConnectionCreate) -> Connection:
        """Create a new connection"""
        with self.Session() as session:
            connection_dict = connection_data.model_dump()
            connection_orm = ConnectionORM(
                **connection_dict, user_id=self.user_id, world_id=self.world_id
            )
            session.add(connection_orm)
            session.commit()
            session.refresh(connection_orm)
            return Connection.model_validate(connection_orm)

    def update_connection(
        self, connection_id: int, connection_update: ConnectionUpdate
    ) -> Connection | None:
        """Update an existing connection for the current user and world"""
        with self.Session() as session:
            connection_orm = (
                session.query(ConnectionORM)
                .filter(
                    ConnectionORM.id == connection_id,
                    ConnectionORM.user_id == self.user_id,
                    ConnectionORM.world_id == self.world_id,
                )
                .first()
            )
            if not connection_orm:
                return None

            # Update fields
            update_data = connection_update.model_dump(
                exclude_unset=True, exclude={"id"}
            )
            for key, value in update_data.items():
                setattr(connection_orm, key, value)

            session.commit()
            session.refresh(connection_orm)
            return Connection.model_validate(connection_orm)

    def delete_connection(self, connection_id: int) -> bool:
        """Delete a connection for the current user and world"""
        with self.Session() as session:
            connection_orm = (
                session.query(ConnectionORM)
                .filter(
                    ConnectionORM.id == connection_id,
                    ConnectionORM.user_id == self.user_id,
                    ConnectionORM.world_id == self.world_id,
                )
                .first()
            )
            if not connection_orm:
                return False

            session.delete(connection_orm)
            session.commit()
            return True

    def get_connections_for_encounter(self, encounter_id: int) -> List[Connection]:
        """Get all connections that involve a specific encounter for the current user and world"""
        with self.Session() as session:
            connection_orms = (
                session.query(ConnectionORM)
                .filter(
                    (ConnectionORM.source_encounter_id == encounter_id)
                    | (ConnectionORM.target_encounter_id == encounter_id),
                    ConnectionORM.user_id == self.user_id,
                    ConnectionORM.world_id == self.world_id,
                )
                .all()
            )
            return [
                Connection.model_validate(connection_orm)
                for connection_orm in connection_orms
            ]

    def connection_exists(self, connection_id: int) -> bool:
        """Check if a connection exists for the current user and world"""
        with self.Session() as session:
            return (
                session.query(ConnectionORM)
                .filter(
                    ConnectionORM.id == connection_id,
                    ConnectionORM.user_id == self.user_id,
                    ConnectionORM.world_id == self.world_id,
                )
                .first()
                is not None
            )
