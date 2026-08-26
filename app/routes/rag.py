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
from app.services.answerability import assess_answerability
from app.services.context_builder import build_rag_context
from app.services.generator_provider import get_generator
from app.services.hybrid_search import search_chunks_hybrid
from app.services.rag_generation import generate_if_allowed
from app.services.semantic_answerability import (
    evaluate_semantic_answerability,
)
from app.services.semantic_answerability_provider import (
    get_semantic_answerability_evaluator,
)


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

    decision = assess_answerability(context)

    if decision.reason == "semantic_evaluation_required":
        evaluator = get_semantic_answerability_evaluator()

        if evaluator is not None:
            decision = evaluate_semantic_answerability(
                evaluator=evaluator,
                question=payload.question,
                context=context.text,
            )

    if not decision.can_generate:
        return RagAnswerResponse(
            answer=None,
            abstained=True,
            sources=sources,
        )

    generator = get_generator()

    generation = generate_if_allowed(
        decision=decision,
        generator=generator,
        question=payload.question,
        context=context.text,
    )

    if generation is None:
        return RagAnswerResponse(
            answer=None,
            abstained=True,
            sources=sources,
        )

    return RagAnswerResponse(
        answer=generation.text,
        abstained=False,
        sources=sources,
    )
