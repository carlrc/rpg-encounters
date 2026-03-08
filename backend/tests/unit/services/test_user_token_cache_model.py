#!/usr/bin/env python3
import pytest
from pydantic import ValidationError

from app.services.user_token import TokenUsageCache


def test_parse_usage_hash_valid():
    raw = {
        "available_tokens": "100",
        "last_used_tokens": "15",
        "total_used_tokens": "45",
        "updated_at_epoch": "1730000000",
        "synced_at_epoch": "1729999940",
    }

    parsed = TokenUsageCache.model_validate(raw)

    assert parsed.available_tokens == 100
    assert parsed.last_used_tokens == 15
    assert parsed.total_used_tokens == 45
    assert parsed.updated_at_epoch == 1730000000
    assert parsed.synced_at_epoch == 1729999940
    assert parsed.model_dump() == {
        "available_tokens": 100,
        "last_used_tokens": 15,
        "total_used_tokens": 45,
        "updated_at_epoch": 1730000000,
        "synced_at_epoch": 1729999940,
    }


def test_parse_usage_hash_missing_field_raises():
    raw = {
        "available_tokens": "100",
        "last_used_tokens": "15",
    }

    with pytest.raises(ValidationError):
        TokenUsageCache.model_validate(raw)


def test_parse_usage_hash_invalid_field_type_raises():
    raw = {
        "available_tokens": "one-hundred",
        "last_used_tokens": "15",
        "total_used_tokens": "45",
        "updated_at_epoch": "1730000000",
        "synced_at_epoch": "1729999940",
    }

    with pytest.raises(ValidationError):
        TokenUsageCache.model_validate(raw)
