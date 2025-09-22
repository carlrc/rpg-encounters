from typing import List

from pydantic import BaseModel, Field, field_validator

from app.db.limits import ENCOUNTER_DESCRIPTION_LIMIT, TITLE_LIMIT


class EncounterBase(BaseModel):
    name: str = Field(..., description="Encounter name", max_length=TITLE_LIMIT)
    description: str | None = Field(
        None,
        description="Encounter description",
        max_length=ENCOUNTER_DESCRIPTION_LIMIT,
    )
    position_x: float = Field(..., description="X coordinate on the canvas")
    position_y: float = Field(..., description="Y coordinate on the canvas")
    character_ids: List[int] | None = Field(
        default=None, description="Character IDs in this encounter"
    )
    player_ids: List[int] | None = Field(
        default=None, description="Player IDs in this encounter"
    )

    @field_validator("position_x", "position_y")
    @classmethod
    def validate_position(cls, v):
        if v < -10000 or v > 10000:
            raise ValueError("Position coordinates must be between -10000 and 10000")
        return v


class EncounterCreate(EncounterBase):
    pass


class EncounterWithId(EncounterBase):
    """Encounter model that includes temp ID for canvas save operations"""

    id: int | str  # Can be UUID (temp) or int (database ID)


class EncounterUpdate(EncounterBase):
    """Encounter update model - all fields optional with same validation rules"""

    name: str | None = None
    description: str | None = None
    position_x: float | None = None
    position_y: float | None = None
    character_ids: List[int] | None = None
    player_ids: List[int] | None = None


class Encounter(EncounterBase):
    id: int

    model_config = {"from_attributes": True}
