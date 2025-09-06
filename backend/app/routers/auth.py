from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.session import (
    create_session,
    destroy_session,
    get_current_user,
    get_current_user_id,
)
from app.data.account_store import AccountStore
from app.data.magic_link_store import MagicLinkStore
from app.db.connection import get_async_db_routes_session
from app.models.magic_link import (
    MagicLinkConsume,
    MagicLinkConsumeResponse,
    MagicLinkCreate,
    MagicLinkRequest,
    MagicLinkResponse,
)
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["authentication"])

DEVICE_NONCE_COOKIE = "device_nonce"
DEVICE_NONCE_MAX_AGE = 60 * 60 * 24 * 365  # 1 year


@router.post("/magic/request", response_model=MagicLinkResponse)
async def request_magic_link(
    body: MagicLinkRequest,
    request: Request,
    response: Response,
    session: AsyncSession = Depends(get_async_db_routes_session),
):
    """
    Request a magic link for login. Account must already exist.
    Sets device_nonce cookie for soft device binding.
    """
    try:
        # Find existing account - do not create new accounts
        account_store = AccountStore(user_id=0, session=session)
        account = await account_store.get_by_email(body.email)

        if not account:
            # Always return success to prevent user enumeration
            # But don't actually create a magic link
            return MagicLinkResponse(
                success=True, token=None, message="Magic link sent successfully"
            )

        # Handle device nonce for soft device binding
        device_nonce = request.cookies.get(DEVICE_NONCE_COOKIE)
        set_cookie = False

        magic_link_store = MagicLinkStore(session=session)

        if not device_nonce:
            device_nonce = magic_link_store.generate_token()
            set_cookie = True

        # Create magic link
        raw_token = magic_link_store.generate_token()

        magic_link_data = MagicLinkCreate(
            user_id=account.user_id,
            token_hash=magic_link_store.hash_token(raw_token),
            device_nonce_hash=magic_link_store.hash_token(device_nonce),
            expires_at=magic_link_store.magic_link_expiry(),
            used=False,
            redirect_to=body.redirect_to,
        )

        await magic_link_store.create(magic_link_data)

        # Set device nonce cookie if needed
        if set_cookie:
            response.set_cookie(
                key=DEVICE_NONCE_COOKIE,
                value=device_nonce,
                max_age=DEVICE_NONCE_MAX_AGE,
                secure=True,
                httponly=False,  # Frontend readable for potential future use
                samesite="lax",
                path="/",
            )

        # For testing: return the raw token. In production, this would be emailed.
        return MagicLinkResponse(
            success=True,
            token=raw_token,
            message="Magic link created successfully. In production, this would be emailed.",
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create magic link: {str(e)}",
        )


@router.post("/magic/consume", response_model=MagicLinkConsumeResponse)
async def consume_magic_link(
    body: MagicLinkConsume,
    request: Request,
    session: AsyncSession = Depends(get_async_db_routes_session),
):
    """
    Consume a magic link token to create a user session.
    Requires matching device_nonce cookie.
    """
    if not body.token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Token is required"
        )

    # Check device nonce cookie
    device_nonce = request.cookies.get(DEVICE_NONCE_COOKIE)
    if not device_nonce:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Device not recognized. Please request a new magic link.",
        )

    # Validate magic link
    magic_link_store = MagicLinkStore(session=session)
    token_hash = magic_link_store.hash_token(body.token)
    device_nonce_hash = magic_link_store.hash_token(device_nonce)

    is_valid, magic_link = await magic_link_store.is_valid_token(
        token_hash, device_nonce_hash
    )

    if not is_valid or not magic_link:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired token"
        )

    # Additional device nonce validation (not implemented in is_valid_token)
    # We need to get the magic link from DB to check device_nonce_hash
    stored_magic_link = await magic_link_store.get_by_token_hash(token_hash)
    if (
        not stored_magic_link
        or stored_magic_link.device_nonce_hash != device_nonce_hash
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Device mismatch. Please use the same device that requested the magic link.",
        )

    # Mark magic link as used
    success = await magic_link_store.mark_used(token_hash)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token has already been used or expired",
        )

    # Create session
    create_session(request, magic_link.user_id)

    return MagicLinkConsumeResponse(
        success=True,
        redirect_to=magic_link.redirect_to,
        message="Successfully authenticated",
    )


@router.post("/logout")
async def logout(request: Request):
    """Logout by destroying the session"""
    destroy_session(request)
    return {"success": True, "message": "Logged out successfully"}


@router.get("/me", response_model=User)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current authenticated user information"""
    return current_user


@router.get("/status")
async def auth_status(request: Request):
    """Check authentication status without requiring login"""
    user_id = get_current_user_id(request)
    return {"authenticated": user_id is not None, "user_id": user_id}
