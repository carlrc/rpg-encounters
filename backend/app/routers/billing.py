import logging

from fastapi import APIRouter, Depends, HTTPException, status

from app.data.user_billing_store import UserBillingStore
from app.dependencies import validate_current_user_id
from app.http import INTERNAL_SERVER_ERROR
from app.models.user_billing import UserBilling

router = APIRouter(prefix="/api/billing", tags=["billing"])

logger = logging.getLogger(__name__)


@router.get("/users/{user_id}", response_model=UserBilling)
async def get_user_billing(
    user_id: int, session_user_id: int = Depends(validate_current_user_id)
):
    try:
        if session_user_id != user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

        return await UserBillingStore(user_id=user_id).get_or_create(user_id=user_id)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get billing for user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=INTERNAL_SERVER_ERROR,
        )
