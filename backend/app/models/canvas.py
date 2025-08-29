from typing import List

from pydantic import BaseModel, Field

from app.models.encounter import Encounter, EncounterWithId
from app.models.encounter_connection import (
    Connection,
    ConnectionCreate,
    ConnectionUpdate,
)


class CanvasSaveRequest(BaseModel):
    """Unified request to save entire canvas state"""

    new_encounters: List[EncounterWithId] = Field(default_factory=list)
    existing_encounters: List[EncounterWithId] = Field(default_factory=list)
    new_connections: List[ConnectionCreate] = Field(default_factory=list)
    existing_connections: List[ConnectionUpdate] = Field(default_factory=list)
    deleted_encounter_ids: List[int] = Field(default_factory=list)
    deleted_connection_ids: List[int] = Field(default_factory=list)


class CanvasResponse(BaseModel):
    """Response with complete canvas state - same structure as encounters endpoint"""

    encounters: List[Encounter]
    connections: List[Connection]
