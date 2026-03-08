from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from app.data.account_store import AccountStore
from app.data.user_billing_store import UserBillingStore
from app.models.user_billing import UserBillingUpdate
from app.services.user_token import UserTokenService

router = APIRouter(prefix="/internal/test", tags=["internal-test"])


class BillingAdjustRequest(BaseModel):
    email: str = Field(...)
    available_tokens: int
    last_used_tokens: int
    total_used_tokens: int | None = Field(default=None)


class BillingSnapshot(BaseModel):
    user_id: int
    available_tokens: int
    last_used_tokens: int
    total_used_tokens: int


@router.post("/billing", response_model=BillingSnapshot, include_in_schema=False)
async def set_billing_state(payload: BillingAdjustRequest) -> BillingSnapshot:
    account = await AccountStore(user_id=None).get_by_email(email=payload.email.strip())
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found for provided email.",
        )
    user_id = account.user_id

    store = UserBillingStore(user_id=user_id)
    existing = await store.get_or_create(user_id=user_id)
    next_total = (
        existing.total_used_tokens
        if payload.total_used_tokens is None
        else payload.total_used_tokens
    )

    await store.update_by_user_id(
        user_id=user_id,
        user_billing_update=UserBillingUpdate(
            available_tokens=payload.available_tokens,
            last_used_tokens=payload.last_used_tokens,
            total_used_tokens=next_total,
        ),
    )
    token_service = UserTokenService()
    await token_service.overwrite_cache_from_db(user_id=user_id)
    usage = await token_service.get_token_usage_summary(user_id=user_id)

    return BillingSnapshot(
        user_id=user_id,
        available_tokens=usage.available_tokens,
        last_used_tokens=usage.last_used_tokens,
        total_used_tokens=usage.total_used_tokens,
    )
