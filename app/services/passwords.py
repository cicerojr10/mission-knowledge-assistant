from pwdlib import PasswordHash


_password_hash = PasswordHash.recommended()


def hash_password(password: str) -> str:
    """
    Gera um hash seguro para uma senha em texto puro.

    A senha original nunca deve ser persistida.
    """
    return _password_hash.hash(password)


def verify_password(
    plain_password: str,
    password_hash: str,
) -> bool:
    """
    Verifica uma senha recebida contra um hash armazenado.
    """
    return _password_hash.verify(
        plain_password,
        password_hash,
    )
