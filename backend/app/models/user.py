from datetime import datetime

from pydantic import BaseModel


class UserBase(BaseModel):
    """Base user model - empty since UserORM only has auto-generated fields"""

    pass


class UserCreate(UserBase):
    """User creation model - empty, user is created with auto-generated id and timestamp"""

    pass


class UserUpdate(UserBase):
    """User update model"""

    pass


class User(UserBase):
    """Complete user model with id and created_at"""

    id: int
    created_at: datetime

    model_config = {"from_attributes": True}
