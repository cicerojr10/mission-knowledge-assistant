from fastapi import APIRouter, Depends

from app.dependencies.auth import get_current_user
from app.models import User as UserModel
from app.schemas import RagAnswerRequest, RagAnswerResponse


router = APIRouter(prefix="/rag", tags=["rag"])


@router.post(
    "/answer",
    response_model=RagAnswerResponse,
)
def answer_question(
    payload: RagAnswerRequest,
    current_user: UserModel = Depends(get_current_user),
):
    if current_user.id is None:
        raise RuntimeError(
            "Authenticated user does not have a persisted ID."
        )

    return RagAnswerResponse(
        answer=None,
        abstained=True,
        sources=[],
    )
