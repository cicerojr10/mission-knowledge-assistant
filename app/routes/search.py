import logging

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session, select

from app.database import get_session
from app.models import Chunk as ChunkModel
from app.models import Document as DocumentModel
from app.schemas import (
    SearchResultResponse,
    SemanticSearchResultResponse,
)
from app.services.semantic_search import search_chunks_semantically


router = APIRouter(prefix="/search", tags=["search"])
logger = logging.getLogger(__name__)


@router.get("", response_model=list[SearchResultResponse])
def search_chunks(
    q: str = Query(..., min_length=1),
    session: Session = Depends(get_session),
):
    clean_query = q.strip()

    if not clean_query:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Search query cannot be empty.",
        )

    statement = (
        select(ChunkModel, DocumentModel)
        .where(ChunkModel.document_id == DocumentModel.id)
        .where(ChunkModel.content.ilike(f"%{clean_query}%"))
        .order_by(DocumentModel.id, ChunkModel.chunk_index)
    )

    results = session.exec(statement).all()

    logger.info(
        "Search executed: query=%s result_count=%s",
        clean_query,
        len(results),
    )

    return [
        SearchResultResponse(
            chunk_id=str(chunk.id),
            document_id=str(document.id),
            document_title=document.title,
            content=chunk.content,
            chunk_index=chunk.chunk_index,
            char_count=chunk.char_count,
        )
        for chunk, document in results
    ]


@router.get(
    "/semantic",
    response_model=list[SemanticSearchResultResponse],
)
def semantic_search_chunks(
    q: str = Query(..., min_length=1),
    top_k: int = Query(default=5, ge=1, le=20),
    session: Session = Depends(get_session),
):
    clean_query = q.strip()

    if not clean_query:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Search query cannot be empty.",
        )

    results = search_chunks_semantically(
        session=session,
        query=clean_query,
        top_k=top_k,
    )

    logger.info(
        "Semantic search executed: query=%s top_k=%s result_count=%s",
        clean_query,
        top_k,
        len(results),
    )

    return [
        SemanticSearchResultResponse(
            chunk_id=str(chunk.id),
            document_id=str(document.id),
            document_title=document.title,
            content=chunk.content,
            chunk_index=chunk.chunk_index,
            char_count=chunk.char_count,
            distance=float(distance),
        )
        for chunk, document, distance in results
    ]
