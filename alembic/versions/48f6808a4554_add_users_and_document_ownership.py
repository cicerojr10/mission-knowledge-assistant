"""add users and document ownership

Revision ID: 48f6808a4554
Revises: 89dabf48a6bd
Create Date: 2026-07-30 21:33:55.772010
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "48f6808a4554"
down_revision: Union[str, Sequence[str], None] = "89dabf48a6bd"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create users and add transitional document ownership."""

    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("email", sa.String(), nullable=False),
        sa.Column("password_hash", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
    )

    op.add_column(
        "document",
        sa.Column("owner_id", sa.Integer(), nullable=True),
    )

    op.create_index(
        op.f("ix_document_owner_id"),
        "document",
        ["owner_id"],
        unique=False,
    )

    op.create_foreign_key(
        "fk_document_owner_id_users",
        "document",
        "users",
        ["owner_id"],
        ["id"],
    )


def downgrade() -> None:
    """Remove transitional document ownership and users."""

    op.drop_constraint(
        "fk_document_owner_id_users",
        "document",
        type_="foreignkey",
    )

    op.drop_index(
        op.f("ix_document_owner_id"),
        table_name="document",
    )

    op.drop_column("document", "owner_id")
    op.drop_table("users")
