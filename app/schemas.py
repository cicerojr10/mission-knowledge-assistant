from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str
    service: str


class DocumentCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=120)
    content: str = Field(..., min_length=1)


class DocumentResponse(BaseModel):
    id: str
    title: str
    content: str