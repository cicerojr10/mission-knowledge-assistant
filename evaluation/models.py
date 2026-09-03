from dataclasses import dataclass
from enum import StrEnum


class EvaluationCategory(StrEnum):
    ANSWERABLE = "answerable"
    UNANSWERABLE = "unanswerable"
    CROSS_USER = "cross_user"
    DIFFICULT = "difficult"


@dataclass(frozen=True)
class EvaluationDocument:
    key: str
    owner_key: str
    title: str
    content: str


@dataclass(frozen=True)
class EvaluationCase:
    id: str
    category: EvaluationCategory
    owner_key: str
    question: str
    expected_abstained: bool
    expected_document_keys: tuple[str, ...]
    forbidden_document_keys: tuple[str, ...]
    reference_answer: str | None = None


@dataclass(frozen=True)
class EvaluationObservation:
    abstained: bool
    document_keys: tuple[str, ...]
    answer: str | None = None


@dataclass(frozen=True)
class EvaluationResult:
    case_id: str
    category: EvaluationCategory
    passed: bool
    abstention_matches: bool
    expected_documents_found: bool
    forbidden_documents_absent: bool
