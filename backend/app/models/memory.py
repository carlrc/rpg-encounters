from typing import List

from pydantic import BaseModel, Field, field_validator

CONTENT_LIMIT = 200


class MemoryBase(BaseModel):
    title: str = Field(..., description="Title of the memory")
    content: str = Field(..., description="Static memories to assign to characters")
    character_ids: List[int]

    @field_validator("content")
    @classmethod
    def validate_content_word_count(cls, content_text):
        if content_text:
            word_count = len(content_text.split())
            if word_count > CONTENT_LIMIT:
                raise ValueError(f"Content must be {CONTENT_LIMIT} words or less")
        return content_text


class MemoryCreate(MemoryBase):
    pass


class MemoryUpdate(MemoryBase):
    pass


class Memory(MemoryBase):
    id: int
