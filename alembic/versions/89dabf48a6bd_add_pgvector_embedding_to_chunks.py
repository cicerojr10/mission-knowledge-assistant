"""add pgvector embedding to chunks

Revision ID: 89dabf48a6bd
Revises: 3da00ef760c0
Create Date: 2026-07-10 23:10:48.980050

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from pgvector.sqlalchemy import VECTOR


# revision identifiers, used by Alembic.
revision: str = "89dabf48a6bd"
down_revision: Union[str, Sequence[str], None] = "3da00ef760c0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Enable pgvector and add the nullable embedding column."""
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    op.add_column(
        "chunks",
        sa.Column(
            "embedding",
            VECTOR(384),
            nullable=True,
        ),
    )


def downgrade() -> None:
    """Remove the embedding column and disable pgvector."""
    op.drop_column("chunks", "embedding")

    op.execute("DROP EXTENSION IF EXISTS vector")