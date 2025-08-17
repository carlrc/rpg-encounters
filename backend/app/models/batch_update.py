from typing import List

from pydantic import BaseModel, Field

from .encounter import Encounter, EncounterCreate, EncounterUpdate, EncounterWithTempId
from .encounter_connection import Connection, ConnectionCreate, ConnectionUpdate


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


class CanvasSaveRequest(BaseModel):
    """Unified request to save entire canvas state"""

    new_encounters: List[EncounterWithTempId] = Field(default_factory=list)
    existing_encounters: List[EncounterUpdate] = Field(default_factory=list)
    new_connections: List[ConnectionCreate] = Field(default_factory=list)
    existing_connections: List[ConnectionUpdate] = Field(default_factory=list)


class CanvasSaveResponse(BaseModel):
    """Response with complete canvas state - same structure as encounters endpoint"""

    encounters: List[Encounter]
    connections: List[Connection]
