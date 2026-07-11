from pgvector.sqlalchemy import VECTOR
from sqlalchemy import Column
from sqlmodel import Field, Relationship, SQLModel


class Document(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str
    content: str

    chunks: list["Chunk"] = Relationship(
        back_populates="document",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )


class Chunk(SQLModel, table=True):
    __tablename__ = "chunks"

    id: int | None = Field(default=None, primary_key=True)
    document_id: int = Field(foreign_key="document.id")
    content: str
    chunk_index: int
    char_count: int
    embedding: list[float] | None = Field(
        default=None,
        sa_column=Column(VECTOR(384), nullable=True),
)

    document: Document = Relationship(back_populates="chunks")