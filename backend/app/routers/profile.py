import logging

from fastapi import APIRouter, Depends, HTTPException, status

from app.dependencies import validate_current_user_id
from app.http import INTERNAL_SERVER_ERROR
from app.models.user_billing import UserBillingBase
from app.services.user_token import UserTokenService

router = APIRouter(prefix="/api/profile", tags=["profile"])
logger = logging.getLogger(__name__)


@router.get("", response_model=UserBillingBase)
async def get_profile(session_user_id: int = Depends(validate_current_user_id)):
    try:
        usage = await UserTokenService().get_token_usage_summary(
            user_id=session_user_id
        )
        return UserBillingBase(
            user_id=session_user_id,
            available_tokens=usage.available_tokens,
            last_used_tokens=usage.last_used_tokens,
            total_used_tokens=usage.total_used_tokens,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get profile for user {session_user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=INTERNAL_SERVER_ERROR,
        )
