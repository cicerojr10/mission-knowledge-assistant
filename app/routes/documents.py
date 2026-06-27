import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.chunker import split_text
from app.config import settings
from app.database import get_session
from app.models import Chunk as ChunkModel
from app.models import Document as DocumentModel
from app.schemas import ChunkResponse, DocumentCreate, DocumentResponse

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

    chunk_contents = split_text(clean_content)
    chunk_count = len(chunk_contents)

    try:
        session.add(document)
        session.flush()

        for chunk_index, chunk_content in enumerate(chunk_contents):
            chunk = ChunkModel(
                document_id=document.id,
                content=chunk_content,
                chunk_index=chunk_index,
                char_count=len(chunk_content),
            )
            session.add(chunk)

        session.commit()
        session.refresh(document)
    except Exception:
        session.rollback()
        logger.exception("Failed to create document with chunks")
        raise

    logger.info(
        "Document created successfully in PostgreSQL: id=%s title=%s chunk_count=%s",
        document.id,
        document.title,
        chunk_count,
    )

    return DocumentResponse(
        id=str(document.id),
        title=document.title,
        content=document.content,
        chunk_count=chunk_count,
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
            chunk_count=len(document.chunks),
        )
        for document in documents
    ]


@router.get("/{document_id}/chunks", response_model=list[ChunkResponse])
def list_document_chunks(
    document_id: int,
    session: Session = Depends(get_session),
):
    document = session.get(DocumentModel, document_id)

    if document is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found.",
        )

    chunks = session.exec(
        select(ChunkModel)
        .where(ChunkModel.document_id == document_id)
        .order_by(ChunkModel.chunk_index)
    ).all()

    logger.info(
        "Listing chunks for document: document_id=%s chunk_count=%s",
        document_id,
        len(chunks),
    )

    return [
        ChunkResponse(
            id=str(chunk.id),
            document_id=str(chunk.document_id),
            content=chunk.content,
            chunk_index=chunk.chunk_index,
            char_count=chunk.char_count,
        )
        for chunk in chunks
    ]
