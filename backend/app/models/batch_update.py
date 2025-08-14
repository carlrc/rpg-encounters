from typing import List

from pydantic import BaseModel

from .encounter import EncounterCreate, EncounterUpdate
from .encounter_connection import ConnectionCreate, ConnectionUpdate


class BatchCreateEncountersRequest(BaseModel):
    """Request to create multiple encounters"""

    encounters: List[EncounterCreate]


class BatchUpdateEncountersRequest(BaseModel):
    """Request to update multiple encounters"""

    encounters: List[EncounterUpdate]


class BatchDeleteEncountersRequest(BaseModel):
    """Request to delete multiple encounters"""

    encounter_ids: List[int]


class BatchCreateConnectionsRequest(BaseModel):
    """Request to create multiple connections"""

    connections: List[ConnectionCreate]


class BatchUpdateConnectionsRequest(BaseModel):
    """Request to update multiple connections"""

    connections: List[ConnectionUpdate]


class BatchDeleteConnectionsRequest(BaseModel):
    """Request to delete multiple connections"""

    connection_ids: List[int]
