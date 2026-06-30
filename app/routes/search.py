import logging

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session, select

from app.database import get_session
from app.models import Chunk as ChunkModel
from app.models import Document as DocumentModel
from app.schemas import SearchResultResponse

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