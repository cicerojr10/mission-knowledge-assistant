import pytest
from pydantic import ValidationError

from app.schemas import UserCreate, UserResponse


MINIMUM_VALID_PASSWORD = "a" * 15


def test_user_create_normalizes_email():
    payload = UserCreate(
        email="  Cicero@Example.COM  ",
        password=MINIMUM_VALID_PASSWORD,
    )

    assert payload.email == "cicero@example.com"


def test_user_create_preserves_password_exactly():
    password_with_spaces = " secure phrase "

    payload = UserCreate(
        email="user@example.com",
        password=password_with_spaces,
    )

    assert (
        payload.password.get_secret_value()
        == password_with_spaces
    )


def test_user_create_rejects_invalid_email():
    with pytest.raises(ValidationError):
        UserCreate(
            email="not-an-email",
            password=MINIMUM_VALID_PASSWORD,
        )


def test_user_create_rejects_password_shorter_than_15_characters():
    with pytest.raises(
        ValidationError,
        match="Password must contain at least 15 characters",
    ):
        UserCreate(
            email="user@example.com",
            password="a" * 14,
        )


def test_user_create_accepts_password_with_15_characters():
    payload = UserCreate(
        email="user@example.com",
        password="a" * 15,
    )

    assert len(payload.password.get_secret_value()) == 15


def test_user_create_accepts_password_with_128_characters():
    payload = UserCreate(
        email="user@example.com",
        password="a" * 128,
    )

    assert len(payload.password.get_secret_value()) == 128


def test_user_create_rejects_password_longer_than_128_characters():
    with pytest.raises(
        ValidationError,
        match="Password must contain at most 128 characters",
    ):
        UserCreate(
            email="user@example.com",
            password="a" * 129,
        )


def test_user_response_does_not_expose_password_fields():
    response = UserResponse(
        id="1",
        email="user@example.com",
    )

    assert response.model_dump() == {
        "id": "1",
        "email": "user@example.com",
    }
