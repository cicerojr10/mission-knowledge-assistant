from sqlmodel import Field, SQLModel


class Document(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str
    content: str