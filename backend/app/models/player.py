from pydantic import BaseModel
from typing import Optional

class PlayerBase(BaseModel):
    name: str
    description: str

class PlayerCreate(PlayerBase):
    pass

class PlayerUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

class Player(PlayerBase):
    id: int
    
    class Config:
        from_attributes = True
