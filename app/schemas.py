from pydantic import BaseModel, Field


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
