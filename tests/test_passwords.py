from app.services.passwords import hash_password, verify_password


TEST_PASSWORD = "uma senha longa e segura"


def test_hash_password_does_not_return_plaintext():
    password_hash = hash_password(TEST_PASSWORD)

    assert password_hash != TEST_PASSWORD
    assert password_hash.startswith("$argon2id$")


def test_hash_password_uses_unique_salt():
    first_hash = hash_password(TEST_PASSWORD)
    second_hash = hash_password(TEST_PASSWORD)

    assert first_hash != second_hash

    assert verify_password(TEST_PASSWORD, first_hash) is True
    assert verify_password(TEST_PASSWORD, second_hash) is True


def test_verify_password_accepts_correct_password():
    password_hash = hash_password(TEST_PASSWORD)

    assert verify_password(TEST_PASSWORD, password_hash) is True


def test_verify_password_rejects_wrong_password():
    password_hash = hash_password(TEST_PASSWORD)

    assert verify_password(
        "uma senha diferente",
        password_hash,
    ) is False
