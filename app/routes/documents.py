import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.config import settings
from app.database import get_session
from app.models import Document as DocumentModel
from app.schemas import DocumentCreate, DocumentResponse

router = APIRouter(prefix="/documents", tags=["documents"])
logger = logging.getLogger(__name__)


@router.post("", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
def create_document(
    payload: DocumentCreate,
    session: Session = Depends(get_session),
):
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

    document = DocumentModel(
        title=clean_title,
        content=clean_content,
    )

    session.add(document)
    session.commit()
    session.refresh(document)

    logger.info(
        "Document created successfully in PostgreSQL: id=%s title=%s",
        document.id,
        document.title,
    )

    return DocumentResponse(
        id=str(document.id),
        title=document.title,
        content=document.content,
    )


@router.get("", response_model=list[DocumentResponse])
def list_documents(
    session: Session = Depends(get_session),
):
    documents = session.exec(select(DocumentModel)).all()

    logger.info("Listing documents from PostgreSQL: count=%s", len(documents))

    return [
        DocumentResponse(
            id=str(document.id),
            title=document.title,
            content=document.content,
        )
        for document in documents
    ]