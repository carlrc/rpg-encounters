import logging
from urllib.parse import urlparse

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.session import (
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
from app.models.magic_link import (
    MagicLinkCreate,
    MagicLinkRequest,
)

router = APIRouter(prefix="/auth", tags=["authentication"])
logger = logging.getLogger(__name__)

DEVICE_NONCE_COOKIE = "device_nonce"
DEVICE_NONCE_MAX_AGE = 60 * 60 * 24 * 365  # 1 year
INVALID_TOKEN = "Invalid or expired token"
DEVICE_MISMATCH = "Login link requested from a different device."


def is_safe_redirect_url(url: str) -> bool:
    """
    Validate that redirect URL is safe to prevent open redirect attacks.
    Only allows relative paths or URLs from the same origin.
    """
    # Allow relative URLs (starting with /)
    if url.startswith("/") and not url.startswith("//"):
        return True

    # Parse the URL to check if it's absolute
    try:
        parsed = urlparse(url)
        # Reject absolute URLs with schemes (http, https, etc.)
        if parsed.scheme or parsed.netloc:
            logger.warning(f"Rejected absolute redirect URL: {url}")
            return False
        return True
    except Exception:
        logger.warning(f"Invalid redirect URL format: {url}")
        return False


@router.post("/request")
async def request_magic_link(
    body: MagicLinkRequest,
    request: Request,
    response: Response,
    session: AsyncSession = Depends(get_async_db_routes_session),
):
    """
    Request a magic link for login. Account must already exist.
    Sets device_nonce cookie for device binding.
    Returns empty 200 response to prevent user enumeration.
    """
    # Validate redirect URL to prevent open redirect attacks
    if not is_safe_redirect_url(body.redirect_to):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid redirect URL. Only relative paths are allowed.",
        )

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

        # Generate new device nonce for strict device binding
        magic_link_store = MagicLinkStore(session=session)
        device_nonce = MagicLinkStore.generate_token()

        # Create magic link
        raw_token = MagicLinkStore.generate_token()

        magic_link_data = MagicLinkCreate(
            user_id=account.user_id,
            token_hash=MagicLinkStore.hash_token(raw_token),
            device_nonce_hash=MagicLinkStore.hash_token(device_nonce),
            expires_at=MagicLinkStore.magic_link_expiry(),
            used=False,
            redirect_to=body.redirect_to,
        )

        await magic_link_store.create(magic_link_data)

        # Always set new device nonce cookie for strict device binding
        response.set_cookie(
            key=DEVICE_NONCE_COOKIE,
            value=device_nonce,
            max_age=DEVICE_NONCE_MAX_AGE,
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

        return RedirectResponse(url=magic_link.redirect_to, status_code=302)

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


@router.post("/logout")
async def logout(request: Request):
    """Logout by destroying the session"""
    destroy_session(request)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
