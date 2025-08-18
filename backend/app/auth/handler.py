import os
from datetime import datetime, timedelta, timezone
from typing import Annotated, Optional

from fastapi import Depends, HTTPException, Query, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from pydantic import ValidationError

from app.auth.token import TokenData
from app.data.user_store import UserStore
from app.models.user import User

# TODO: Leaving this here as reference for now

"""
References:
- OAuth2 with Password and JWT Bearer (FastAPI docs): https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/
- Get Current User via dependency injection (FastAPI docs): https://fastapi.tiangolo.com/tutorial/security/get-current-user/
- BackgroundTasks for sending emails (e.g., magic links): https://fastapi.tiangolo.com/tutorial/background-tasks/
"""

SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
MAGIC_LINK_EXPIRE_MINUTES = int(os.getenv("MAGIC_LINK_EXPIRE_MINUTES", "15"))

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def _expire_at(minutes: int) -> datetime:
    return datetime.now(timezone.utc) + timedelta(minutes=minutes)


def create_magic_link_token(email: str, *, minutes: Optional[int] = None) -> str:
    """
    Create a short-lived JWT to embed in a magic-link.
    Use when emailing login links. Store subject as email.
    """
    exp_minutes = minutes if minutes is not None else MAGIC_LINK_EXPIRE_MINUTES
    to_encode = {
        "sub": email,
        "purpose": "magic_link",
        "exp": int(_expire_at(exp_minutes).timestamp()),
    }
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def create_bearer_access_token(subject: str, *, minutes: Optional[int] = None) -> str:
    """
    Create a standard Bearer JWT for use after exchanging a magic link.
    """
    exp_minutes = minutes if minutes is not None else ACCESS_TOKEN_EXPIRE_MINUTES
    to_encode = {
        "sub": subject,
        "purpose": "access",
        "exp": int(_expire_at(exp_minutes).timestamp()),
    }
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def _decode_token(token: str) -> TokenData:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return TokenData(**payload)
    except (JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user_bearer(
    token: Annotated[str, Depends(oauth2_scheme)],
) -> User:
    """
    Router dependency for Authorization: Bearer <token>.
    Use after you have issued a long-lived access token.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = _decode_token(token)
    if payload.purpose != "access":
        raise credentials_exception
    user_id = payload.get("sub")
    if user_id is None:
        raise credentials_exception
    user = UserStore().get_user_by_id()
    if user is None:
        raise credentials_exception
    return user


async def require_magic_link_token(
    token: Annotated[str, Query(..., description="Magic link token in query")],
) -> TokenData:
    """
    Router dependency for magic-link callbacks.
    The link you email should include ?token=<jwt>.
    Example:
      /auth/callback?token=eyJhbGciOiJ...
    """
    payload = _decode_token(token)
    if payload.purpose != "magic_link":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    return payload


# === Minimal usage examples ===
# routers/auth.py
# from fastapi import APIRouter, Depends
# from .auth_tokens import require_magic_link_token, create_bearer_access_token
#
# router = APIRouter(prefix="/auth", tags=["auth"])
#
# @router.get("/callback")
# async def magic_link_callback(tok=Depends(require_magic_link_token)):
#     # Issue normal bearer token for subsequent API calls
#     access = create_bearer_access_token(tok.sub)
#     return {"access_token": access, "token_type": "bearer"}
#
# routers/protected.py
# from fastapi import APIRouter, Depends
# from .auth_tokens import get_current_user_bearer
#
# router = APIRouter(prefix="/protected", tags=["protected"])
#
# @router.get("/me")
# async def me(user=Depends(get_current_user_bearer)):
#     return {"email": user.sub}
