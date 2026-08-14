from typing import Literal

from pydantic import (
    BaseModel,
    EmailStr,
    Field,
    SecretStr,
    field_validator,
)


class UserCreate(BaseModel):
    email: EmailStr
    password: SecretStr

    @field_validator("email", mode="before")
    @classmethod
    def strip_email_whitespace(cls, value: object) -> object:
        if isinstance(value, str):
            return value.strip()

        return value

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        return value.lower()

    @field_validator("password")
    @classmethod
    def validate_password_length(cls, value: SecretStr) -> SecretStr:
        password_length = len(value.get_secret_value())

        if password_length < 15:
            raise ValueError(
                "Password must contain at least 15 characters."
            )

        if password_length > 128:
            raise ValueError(
                "Password must contain at most 128 characters."
            )

        return value


class UserResponse(BaseModel):
    id: str
    email: EmailStr


class LoginRequest(BaseModel):
    email: EmailStr
    password: SecretStr

    @field_validator("email", mode="before")
    @classmethod
    def strip_email_whitespace(cls, value: object) -> object:
        if isinstance(value, str):
            return value.strip()

        return value

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        return value.lower()


class TokenResponse(BaseModel):
    access_token: str = Field(..., min_length=1)
    token_type: Literal["bearer"] = "bearer"


class DocumentCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=120)
    content: str = Field(..., min_length=1)


class DocumentResponse(BaseModel):
    id: str
    title: str
    content: str
    chunk_count: int = 0


class ChunkResponse(BaseModel):
    id: str
    document_id: str
    content: str
    chunk_index: int
    char_count: int


class SearchResultResponse(BaseModel):
    chunk_id: str
    document_id: str
    document_title: str
    content: str
    chunk_index: int
    char_count: int


class SemanticSearchResultResponse(BaseModel):
    chunk_id: str
    document_id: str
    document_title: str
    content: str
    chunk_index: int
    char_count: int
    distance: float


class HybridSearchResultResponse(BaseModel):
    chunk_id: str
    document_id: str
    document_title: str
    content: str
    chunk_index: int
    char_count: int
    rrf_score: float
    textual_rank: int | None
    semantic_rank: int | None
    semantic_distance: float | None


class RagAnswerRequest(BaseModel):
    question: str = Field(
        ...,
        min_length=1,
        max_length=2000,
    )


class RagSourceResponse(BaseModel):
    chunk_id: str
    document_id: str
    document_title: str
    content: str
    chunk_index: int


class RagAnswerResponse(BaseModel):
    answer: str | None
    abstained: bool
    sources: list[RagSourceResponse]
