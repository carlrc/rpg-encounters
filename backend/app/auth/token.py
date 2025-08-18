from pydantic import BaseModel, EmailStr


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    user_id: str
    world_id: str
    sub: EmailStr
    purpose: str
    exp: int
