from dataclasses import dataclass
from typing import Literal


SearchCategory = Literal[
    "literal",
    "paraphrase",
    "identifier",
    "intent",
    "hybrid",
    "no_match",
]


@dataclass(frozen=True)
class EvaluationDocument:
    code: str
    title: str
    content: str


@dataclass(frozen=True)
class EvaluationCase:
    code: str
    category: SearchCategory
    query: str
    expected_document_code: str | None


DOCUMENTS = (
    EvaluationDocument(
        code="DOC-01",
        title="Artemis Program",
        content=(
            "The Artemis program is NASA's initiative to return "
            "astronauts to the lunar surface and establish a "
            "sustainable human presence on the Moon."
        ),
    ),
    EvaluationDocument(
        code="DOC-02",
        title="PostgreSQL Overview",
        content=(
            "PostgreSQL is an open-source relational database "
            "commonly used by backend applications to store and "
            "query structured data."
        ),
    ),
    EvaluationDocument(
        code="DOC-03",
        title="Password Recovery",
        content=(
            "Users who cannot access their account can request a "
            "password reset link by email and create a new password."
        ),
    ),
    EvaluationDocument(
        code="DOC-04",
        title="STS-135 Mission",
        content=(
            "STS-135 was the final mission of NASA's Space Shuttle "
            "program and the last flight of Space Shuttle Atlantis."
        ),
    ),
    EvaluationDocument(
        code="DOC-05",
        title="Upload Error 413",
        content=(
            "HTTP status code 413 indicates that the uploaded file "
            "or request payload is larger than the server allows."
        ),
    ),
)


CASES = (
    EvaluationCase(
        code="CASE-01",
        category="literal",
        query="Artemis",
        expected_document_code="DOC-01",
    ),
    EvaluationCase(
        code="CASE-02",
        category="paraphrase",
        query="How does NASA plan to send people back to the Moon?",
        expected_document_code="DOC-01",
    ),
    EvaluationCase(
        code="CASE-03",
        category="identifier",
        query="STS-135",
        expected_document_code="DOC-04",
    ),
    EvaluationCase(
        code="CASE-04",
        category="intent",
        query=(
            "I cannot sign in to my account. "
            "How can I regain access?"
        ),
        expected_document_code="DOC-03",
    ),
    EvaluationCase(
        code="CASE-05",
        category="hybrid",
        query="Error 413 while uploading a document",
        expected_document_code="DOC-05",
    ),
    EvaluationCase(
        code="CASE-06",
        category="no_match",
        query="How do I prepare pizza dough?",
        expected_document_code=None,
    ),
)


if __name__ == "__main__":
    print(f"documents={len(DOCUMENTS)}")
    print(f"cases={len(CASES)}")

    for case in CASES:
        expected = case.expected_document_code or "NONE"

        print(
            f"{case.code} | "
            f"{case.category} | "
            f"expected={expected}"
        )