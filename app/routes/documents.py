from uuid import uuid4

from fastapi import APIRouter, HTTPException, status

from app.schemas import DocumentCreate, DocumentResponse

router = APIRouter(prefix="/documents", tags=["documents"])

# Armazenamento em memoria apenas para a Semana 1.
# Na Semana 2, isso sera substituido por PostgreSQL.
_DOCUMENTS: list[DocumentResponse] = []


@router.post("", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
def create_document(payload: DocumentCreate):
    clean_content = payload.content.strip()

    if not clean_content:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Document content cannot be empty.",
        )

    document = DocumentResponse(
        id=str(uuid4()),
        title=payload.title.strip(),
        content=clean_content,
    )
    _DOCUMENTS.append(document)
    return document


@router.get("", response_model=list[DocumentResponse])
def list_documents():
    return _DOCUMENTS
