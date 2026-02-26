"""Tests for auth utilities — token creation, decoding, validation."""

import pytest
from datetime import datetime, timezone

from src.auth.utils import (
    create_access_token,
    create_refresh_token,
    create_verify_token,
    decode_token,
)
from src.core.config import settings


class TestTokenCreation:
    def test_access_token_created(self):
        token = create_access_token({"sub": "test@example.com"})
        assert isinstance(token, str)
        assert len(token) > 20

    def test_access_token_decodable(self):
        token = create_access_token({"sub": "test@example.com"})
        payload = decode_token(token)
        assert payload["sub"] == "test@example.com"
        assert payload["type"] == "access"

    def test_refresh_token_created(self):
        token = create_refresh_token({"sub": "test@example.com"})
        payload = decode_token(token)
        assert payload["type"] == "refresh"

    def test_verify_token_created(self):
        token = create_verify_token("test@example.com")
        payload = decode_token(token)
        assert payload["sub"] == "test@example.com"
        assert payload["type"] == "verification"

    def test_token_has_expiry(self):
        token = create_access_token({"sub": "test@example.com"})
        payload = decode_token(token)
        assert "exp" in payload
        assert payload["exp"] > datetime.now(timezone.utc).timestamp()

    def test_invalid_token_raises(self):
        from src.auth.exceptions import UserNotAuthenticated
        with pytest.raises(UserNotAuthenticated):
            decode_token("not.a.valid.token")

    def test_different_users_different_tokens(self):
        t1 = create_access_token({"sub": "user1@test.com"})
        t2 = create_access_token({"sub": "user2@test.com"})
        assert t1 != t2


class TestTokenPayload:
    def test_custom_data_preserved(self):
        token = create_access_token({"sub": "u@t.com", "custom": "data"})
        payload = decode_token(token)
        assert payload["custom"] == "data"

    def test_multiple_fields(self):
        data = {"sub": "u@t.com", "role": "admin", "user_id": "123"}
        token = create_access_token(data)
        payload = decode_token(token)
        assert payload["role"] == "admin"
        assert payload["user_id"] == "123"
