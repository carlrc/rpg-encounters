from typing import List

from pydantic import BaseModel, Field

from app.db.limits import MEMORY_CONTENT_LIMIT, TITLE_LIMIT


class MemoryBase(BaseModel):
    title: str = Field(..., description="Title of the memory", max_length=TITLE_LIMIT)
    content: str = Field(
        ...,
        description="Static memories to assign to characters",
        max_length=MEMORY_CONTENT_LIMIT,
    )
    character_ids: List[int]


class MemoryCreate(MemoryBase):
    pass


class MemoryUpdate(MemoryBase):
    pass


class Memory(MemoryBase):
    id: int
