import pytest
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, delete, select

from app.database import engine
from app.models import Chunk, Document, User


@pytest.fixture(autouse=True)
def clear_user_ownership_data():
    """
    Limpa os dados respeitando a ordem das foreign keys:

    Chunk -> Document -> User
    """
    with Session(engine) as session:
        session.exec(delete(Chunk))
        session.exec(delete(Document))
        session.exec(delete(User))
        session.commit()

    yield

    with Session(engine) as session:
        session.exec(delete(Chunk))
        session.exec(delete(Document))
        session.exec(delete(User))
        session.commit()


def test_user_can_be_persisted():
    with Session(engine) as session:
        user = User(
            email="alice@example.com",
            password_hash="fake-hash-for-model-test",
        )

        session.add(user)
        session.commit()
        session.refresh(user)

        assert user.id is not None

        persisted_user = session.exec(
            select(User).where(User.email == "alice@example.com")
        ).one()

        assert persisted_user.email == "alice@example.com"
        assert persisted_user.password_hash == "fake-hash-for-model-test"


def test_user_email_must_be_unique():
    with Session(engine) as session:
        first_user = User(
            email="duplicate@example.com",
            password_hash="fake-hash-one",
        )
        second_user = User(
            email="duplicate@example.com",
            password_hash="fake-hash-two",
        )

        session.add(first_user)
        session.add(second_user)

        with pytest.raises(IntegrityError):
            session.commit()

        session.rollback()


def test_document_can_be_assigned_to_user():
    with Session(engine) as session:
        user = User(
            email="owner@example.com",
            password_hash="fake-hash-for-owner-test",
        )

        session.add(user)
        session.flush()

        document = Document(
            title="Owned Artemis Document",
            content="Document content owned by a specific user.",
            owner=user,
        )

        session.add(document)
        session.commit()
        session.refresh(user)
        session.refresh(document)

        assert user.id is not None
        assert document.id is not None
        assert document.owner_id == user.id

        assert document.owner is not None
        assert document.owner.id == user.id
        assert document.owner.email == user.email

        owned_document_ids = [
            owned_document.id
            for owned_document in user.documents
        ]

        assert document.id in owned_document_ids


def test_document_rejects_nonexistent_owner():
    with Session(engine) as session:
        user = User(
            email="temporary@example.com",
            password_hash="fake-hash-for-foreign-key-test",
        )

        session.add(user)
        session.commit()
        session.refresh(user)

        deleted_user_id = user.id

        session.delete(user)
        session.commit()

        document = Document(
            title="Invalid ownership",
            content="This document points to a user that no longer exists.",
            owner_id=deleted_user_id,
        )

        session.add(document)

        with pytest.raises(IntegrityError):
            session.commit()

        session.rollback()
