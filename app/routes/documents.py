import logging
from uuid import uuid4

from fastapi import APIRouter, HTTPException, status

from app.config import settings
from app.schemas import DocumentCreate, DocumentResponse

router = APIRouter(prefix="/documents", tags=["documents"])
logger = logging.getLogger(__name__)

# Armazenamento em memória apenas para a Semana 1.
# Na Semana 2, isso será substituído por PostgreSQL.
_DOCUMENTS: list[DocumentResponse] = []


@router.post("", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
def create_document(payload: DocumentCreate):
    clean_title = payload.title.strip()
    clean_content = payload.content.strip()

    if not clean_title:
        logger.warning("Rejected document creation: empty title")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Document title cannot be empty.",
        )

    if not clean_content:
        logger.warning("Rejected document creation: empty content")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Document content cannot be empty.",
        )

    if len(clean_content) > settings.max_document_content_length:
        logger.warning(
            "Rejected document creation: content too long. length=%s max=%s",
            len(clean_content),
            settings.max_document_content_length,
        )
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=(
                "Document content is too large. "
                f"Maximum allowed length is {settings.max_document_content_length} characters."
            ),
        )

    document = DocumentResponse(
        id=str(uuid4()),
        title=clean_title,
        content=clean_content,
    )

    _DOCUMENTS.append(document)

    logger.info(
        "Document created successfully: id=%s title=%s",
        document.id,
        document.title,
    )

    return document


@router.get("", response_model=list[DocumentResponse])
def list_documents():
    logger.info("Listing documents: count=%s", len(_DOCUMENTS))
    return _DOCUMENTS