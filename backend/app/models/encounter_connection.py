from enum import Enum

from pydantic import BaseModel, Field, field_validator

from .util import validate_choice


class EdgeType(str, Enum):
    STRAIGHT = "straight"
    SMOOTH_STEP = "smoothstep"
    STEP = "step"
    BEZIER = "bezier"


class ConnectionHandle(Enum):
    TOP = "top"
    RIGHT = "right"
    BOTTOM = "bottom"
    LEFT = "left"


VALID_CONNECTIONS = [h.value for h in ConnectionHandle]


class ConnectionBase(BaseModel):
    source_encounter_id: int = Field(..., description="Source encounter ID")
    target_encounter_id: int = Field(..., description="Target encounter ID")
    source_handle: str = Field(..., description="Source connection handle")
    target_handle: str = Field(..., description="Target connection handle")
    edge_type: str = Field(EdgeType.STRAIGHT.value, description="Vue Flow edge type")
    stroke_color: str = Field("#007bff", description="Connection line color")
    stroke_width: int = Field(3, description="Connection line width")

    @field_validator("source_handle", "target_handle")
    @classmethod
    def validate_handle(cls, v):
        if v is not None:
            return validate_choice(v, VALID_CONNECTIONS, "Connection")
        return v

    @field_validator("stroke_width")
    @classmethod
    def validate_stroke_width(cls, v):
        if v < 1 or v > 10:
            raise ValueError("Stroke width must be between 1 and 10")
        return v


class ConnectionCreate(ConnectionBase):
    """Connection creation model"""

    pass


class ConnectionUpdate(ConnectionBase):
    """Connection update model - all fields optional"""

    id: int | None = None
    source_encounter_id: int | None = None
    target_encounter_id: int | None = None
    source_handle: str | None = None
    target_handle: str | None = None
    edge_type: str | None = None
    stroke_color: str | None = None
    stroke_width: int | None = None


class Connection(ConnectionBase):
    id: int

    model_config = {"from_attributes": True}
