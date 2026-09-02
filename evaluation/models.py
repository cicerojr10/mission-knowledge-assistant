from dataclasses import dataclass
from enum import StrEnum


class EvaluationCategory(StrEnum):
    ANSWERABLE = "answerable"
    UNANSWERABLE = "unanswerable"
    CROSS_USER = "cross_user"
    DIFFICULT = "difficult"


@dataclass(frozen=True)
class EvaluationCase:
    id: str
    category: EvaluationCategory
    question: str
    expected_abstained: bool
    expected_document_keys: tuple[str, ...]
    forbidden_document_keys: tuple[str, ...]
    reference_answer: str | None = None