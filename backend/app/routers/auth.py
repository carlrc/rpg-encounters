import logging

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.session import (
    IS_LOCAL,
    SESSION_CONFIG,
    destroy_session,
)
from app.data.account_store import AccountStore
from app.data.magic_link_store import (
    DeviceMismatchError,
    MagicLinkStore,
    TokenAlreadyUsedError,
    TokenExpiredError,
    TokenNotFoundError,
)
from app.db.connection import get_async_db_routes_session
from app.dependencies import get_current_user_world
from app.http import DEVICE_MISMATCH, DEVICE_NONCE_COOKIE
from app.models.magic_link import (
    AuthCheckResponse,
    MagicLinkCreate,
    MagicLinkRequest,
)
from app.utils import get_or_throw

router = APIRouter(prefix="/api/auth", tags=["authentication"])
logger = logging.getLogger(__name__)

FRONTEND_URL = get_or_throw("FRONTEND_URL")
BACKEND_REDIRECT_URL = f"{FRONTEND_URL}/players"


@router.post("/request")
async def request_magic_link(
    body: MagicLinkRequest,
    _: Request,
    response: Response,
    session: AsyncSession = Depends(get_async_db_routes_session),
):
    """
    Request a magic link for login. Account must already exist.
    Sets device_nonce cookie for device binding.
    Returns empty 200 response to prevent user enumeration.
    """

    try:
        account = await AccountStore(user_id=None, session=session).get_by_email(
            body.email
        )

        # TODO: This will eventually need to assert on paid aspects of the account
        if not account:
            logger.warning(f"Invalid email {body.email} used to create login link.")
            # Always return 200 to prevent user enumeration
            # But don't actually create a magic link
            return

        magic_link_store = MagicLinkStore(session=session)

        # Generate new device nonce for strict device binding
        device_nonce = MagicLinkStore.generate_token()

        # Create magic link
        raw_token = MagicLinkStore.generate_token()

        # TODO: Raw token would be emailed to users here
        if IS_LOCAL:
            # So you can login manually locally
            logger.info(f"Login link {FRONTEND_URL}/auth?token={raw_token}")
            logger.info(f"Device nonce {device_nonce}")

        magic_link_data = MagicLinkCreate(
            user_id=account.user_id,
            token_hash=MagicLinkStore.hash_token(raw_token),
            device_nonce_hash=MagicLinkStore.hash_token(device_nonce),
            expires_at=MagicLinkStore.magic_link_expiry(),
            used=False,
        )

        await magic_link_store.create(magic_link_data)

        # Always set new device nonce cookie for strict device binding
        response.set_cookie(
            key=DEVICE_NONCE_COOKIE,
            value=device_nonce,
            max_age=SESSION_CONFIG.max_age,
            secure=SESSION_CONFIG.secure,
            httponly=SESSION_CONFIG.httponly,
            path="/",
        )

    except Exception as e:
        logger.error(f"Failed to create magic link for email {body.email}: {e}")
        raise


@router.get("")
async def consume_magic_link(
    token: str,
    request: Request,
    session: AsyncSession = Depends(get_async_db_routes_session),
):
    """
    Consume a magic link token to create a user session and redirect to destination.
    Requires matching device_nonce cookie.
    Token is provided as a query parameter.
    """
    # Check device nonce cookie
    device_nonce = request.cookies.get(DEVICE_NONCE_COOKIE)
    if not device_nonce:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=DEVICE_MISMATCH
        )

    # Validate and consume magic link atomically
    magic_link_store = MagicLinkStore(session=session)
    token_hash = MagicLinkStore.hash_token(token)
    device_nonce_hash = MagicLinkStore.hash_token(device_nonce)

    try:
        magic_link = await magic_link_store.consume(token_hash, device_nonce_hash)

        # Create session
        request.session["user_id"] = magic_link.user_id

        return RedirectResponse(
            url=BACKEND_REDIRECT_URL, status_code=status.HTTP_302_FOUND
        )

    except (
        TokenNotFoundError,
        TokenAlreadyUsedError,
        TokenExpiredError,
        DeviceMismatchError,
    ):
        # Redirect to login page with error instead of returning JSON
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.error(f"Error processing magic link: {e}")
        raise


@router.get("/check", response_model=AuthCheckResponse)
async def check_auth(request: Request) -> AuthCheckResponse:
    """Check if user is authenticated via session."""
    try:
        user_id = request.session.get("user_id")
        return AuthCheckResponse(authenticated=bool(user_id))
    except Exception:
        logger.error(
            f"Could not check authentication status of session: {request.session}"
        )
        raise


@router.post("/logout")
async def logout(
    request: Request, _: tuple[int, int] = Depends(get_current_user_world)
):
    """Logout by destroying the session"""
    destroy_session(request)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
