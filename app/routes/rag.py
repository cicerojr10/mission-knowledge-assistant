from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.database import get_session
from app.dependencies.auth import get_current_user
from app.models import User as UserModel
from app.schemas import (
    RagAnswerRequest,
    RagAnswerResponse,
    RagSourceResponse,
)
from app.services.context_builder import build_rag_context
from app.services.hybrid_search import search_chunks_hybrid


router = APIRouter(prefix="/rag", tags=["rag"])


@router.post(
    "/answer",
    response_model=RagAnswerResponse,
)
def answer_question(
    payload: RagAnswerRequest,
    session: Session = Depends(get_session),
    current_user: UserModel = Depends(get_current_user),
):
    if current_user.id is None:
        raise RuntimeError(
            "Authenticated user does not have a persisted ID."
        )

    results = search_chunks_hybrid(
        session=session,
        query=payload.question,
        top_k=5,
        owner_id=current_user.id,
    )

    context = build_rag_context(results)

    sources = [
        RagSourceResponse(
            chunk_id=str(result.chunk.id),
            document_id=str(result.document.id),
            document_title=result.document.title,
            content=result.chunk.content,
            chunk_index=result.chunk.chunk_index,
        )
        for result in context.evidence
    ]

    return RagAnswerResponse(
        answer=None,
        abstained=True,
        sources=sources,
    )
