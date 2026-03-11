import logging

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status

from app.auth.session import destroy_session
from app.data.user_store import UserStore
from app.dependencies import validate_current_user_id
from app.http import INTERNAL_SERVER_ERROR
from app.models.user_billing import UserBillingBase
from app.services.redis import flush_user_token_usage
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


@router.delete("")
async def delete_account(
    request: Request,
    user_id: int = Depends(validate_current_user_id),
):
    try:
        try:
            await flush_user_token_usage(user_id=user_id)
        except Exception as e:
            logger.error(
                f"Failed to flush billing usage before delete for user {user_id}: {e}"
            )
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE)

        await UserTokenService().clear_cache(user_id=user_id)

        deleted = await UserStore(user_id=user_id).delete()
        if not deleted:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

        destroy_session(request)
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete account for user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=INTERNAL_SERVER_ERROR,
        )
