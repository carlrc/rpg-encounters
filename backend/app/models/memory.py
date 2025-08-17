from typing import List

from pydantic import BaseModel, Field, field_validator

from app.db.limits import MEMORY_CONTENT_LIMIT, MEMORY_TITLE_LIMIT

from .util import validate_character_count


class MemoryBase(BaseModel):
    title: str = Field(..., description="Title of the memory")
    content: str = Field(..., description="Static memories to assign to characters")
    character_ids: List[int]

    @field_validator("title")
    @classmethod
    def validate_title_character_count(cls, v):
        if v is not None:
            return validate_character_count(v, MEMORY_TITLE_LIMIT, "Title")
        return v

    @field_validator("content")
    @classmethod
    def validate_content_character_count(cls, v):
        if v is not None:
            return validate_character_count(v, MEMORY_CONTENT_LIMIT, "Content")
        return v


class MemoryCreate(MemoryBase):
    pass


class MemoryUpdate(MemoryBase):
    pass


class Memory(MemoryBase):
    id: int
