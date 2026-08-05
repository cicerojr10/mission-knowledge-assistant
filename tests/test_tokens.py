from datetime import datetime, timedelta, timezone

import jwt
import pytest
from pydantic import SecretStr

from app.config import settings
from app.services.tokens import (
    InvalidAccessTokenError,
    TokenConfigurationError,
    create_access_token,
    decode_access_token,
)


TEST_JWT_SECRET = (
    "test-only-secret-key-with-enough-length-for-jwt-tests"
)


@pytest.fixture(autouse=True)
def configure_test_jwt(monkeypatch):
    monkeypatch.setattr(
        settings,
        "jwt_secret_key",
        SecretStr(TEST_JWT_SECRET),
    )
    monkeypatch.setattr(
        settings,
        "jwt_algorithm",
        "HS256",
    )
    monkeypatch.setattr(
        settings,
        "jwt_access_token_expire_minutes",
        30,
    )


def test_create_and_decode_access_token():
    token = create_access_token(subject="123")

    subject = decode_access_token(token)

    assert subject == "123"


def test_decode_access_token_rejects_expired_token():
    token = create_access_token(
        subject="123",
        expires_delta=timedelta(seconds=-1),
    )

    with pytest.raises(InvalidAccessTokenError):
        decode_access_token(token)


def test_decode_access_token_rejects_tampered_token():
    token = create_access_token(subject="123")
    tampered_token = f"{token}tampered"

    with pytest.raises(InvalidAccessTokenError):
        decode_access_token(tampered_token)


def test_decode_access_token_requires_subject_claim():
    issued_at = datetime.now(timezone.utc)

    token = jwt.encode(
        {
            "iat": issued_at,
            "exp": issued_at + timedelta(minutes=5),
        },
        TEST_JWT_SECRET,
        algorithm="HS256",
    )

    with pytest.raises(InvalidAccessTokenError):
        decode_access_token(token)


def test_create_access_token_requires_secret(monkeypatch):
    monkeypatch.setattr(
        settings,
        "jwt_secret_key",
        None,
    )

    with pytest.raises(
        TokenConfigurationError,
        match="JWT_SECRET_KEY is not configured",
    ):
        create_access_token(subject="123")
