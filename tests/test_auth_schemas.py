import pytest
from pydantic import ValidationError

from app.schemas import LoginRequest, TokenResponse


def test_login_request_normalizes_email():
    payload = LoginRequest(
        email="  User@Example.COM  ",
        password="any-login-password",
    )

    assert str(payload.email) == "user@example.com"


def test_login_request_keeps_password_secret():
    payload = LoginRequest(
        email="user@example.com",
        password="any-login-password",
    )

    assert str(payload.password) == "**********"
    assert (
        payload.password.get_secret_value()
        == "any-login-password"
    )


def test_login_request_rejects_invalid_email():
    with pytest.raises(ValidationError):
        LoginRequest(
            email="invalid-email",
            password="any-login-password",
        )


def test_token_response_uses_bearer_type_by_default():
    response = TokenResponse(access_token="signed-jwt-token")

    assert response.access_token == "signed-jwt-token"
    assert response.token_type == "bearer"


def test_token_response_rejects_empty_access_token():
    with pytest.raises(ValidationError):
        TokenResponse(access_token="")
