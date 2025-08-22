from datetime import datetime

from pydantic import BaseModel


class WorldBase(BaseModel):
    """Base world model - empty since WorldORM only has auto-generated fields"""

    pass


class WorldCreate(WorldBase):
    """World creation model - empty, world is created with auto-generated id and timestamp"""

    pass


class WorldUpdate(WorldBase):
    """World update model - currently no updatable fields"""

    pass


class World(WorldBase):
    """Complete world model with id, user_id and created_at"""

    id: int
    user_id: int
    created_at: datetime

    model_config = {"from_attributes": True}
