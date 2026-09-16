from dataclasses import dataclass
from uuid import uuid4

from sqlmodel import Session, delete

from app.chunker import split_text
from app.models import Chunk, Document, User
from app.services.embeddings import generate_embeddings
from app.services.hybrid_search import (
    HybridSearchResult,
    search_chunks_hybrid,
)
from app.services.passwords import hash_password
from evaluation.models import (
    EvaluationCase,
    EvaluationDocument,
)


@dataclass(frozen=True)
class SeededEvaluationCorpus:
    owner_ids: dict[str, int]
    document_keys_by_id: dict[int, str]
    document_ids: tuple[int, ...]
    user_ids: tuple[int, ...]


@dataclass(frozen=True)
class RetrievalObservation:
    document_keys: tuple[str, ...]
    results: tuple[HybridSearchResult, ...] = ()


def seed_evaluation_corpus(
    session: Session,
    documents: list[EvaluationDocument],
) -> SeededEvaluationCorpus:
    run_id = uuid4().hex

    owner_keys = sorted(
        {
            document.owner_key
            for document in documents
        }
    )

    owner_ids: dict[str, int] = {}
    user_ids: list[int] = []
    document_keys_by_id: dict[int, str] = {}
    document_ids: list[int] = []

    try:
        password_hash = hash_password(
            f"evaluation-only-{run_id}"
        )

        for owner_key in owner_keys:
            user = User(
                email=(
                    f"evaluation-{run_id}-"
                    f"{owner_key}@example.com"
                ),
                password_hash=password_hash,
            )

            session.add(user)
            session.flush()

            if user.id is None:
                raise RuntimeError(
                    "Evaluation user ID was not generated."
                )

            owner_ids[owner_key] = user.id
            user_ids.append(user.id)

        chunk_specs: list[
            tuple[int, int, str]
        ] = []

        for evaluation_document in documents:
            owner_id = owner_ids[
                evaluation_document.owner_key
            ]

            document = Document(
                title=evaluation_document.title,
                content=evaluation_document.content,
                owner_id=owner_id,
            )

            session.add(document)
            session.flush()

            if document.id is None:
                raise RuntimeError(
                    "Evaluation document ID "
                    "was not generated."
                )

            document_keys_by_id[
                document.id
            ] = evaluation_document.key

            document_ids.append(document.id)

            chunk_contents = split_text(
                evaluation_document.content
            )

            if not chunk_contents:
                raise ValueError(
                    "Evaluation document "
                    f"{evaluation_document.key!r} "
                    "produced no chunks."
                )

            for chunk_index, content in enumerate(
                chunk_contents
            ):
                chunk_specs.append(
                    (
                        document.id,
                        chunk_index,
                        content,
                    )
                )

        embeddings = generate_embeddings(
            [
                content
                for _, _, content in chunk_specs
            ]
        )

        for (
            document_id,
            chunk_index,
            content,
        ), embedding in zip(
            chunk_specs,
            embeddings,
            strict=True,
        ):
            chunk = Chunk(
                document_id=document_id,
                content=content,
                chunk_index=chunk_index,
                char_count=len(content),
                embedding=embedding,
            )

            session.add(chunk)

        session.commit()

    except Exception:
        session.rollback()
        raise

    return SeededEvaluationCorpus(
        owner_ids=owner_ids,
        document_keys_by_id=(
            document_keys_by_id
        ),
        document_ids=tuple(document_ids),
        user_ids=tuple(user_ids),
    )


def execute_retrieval_case(
    session: Session,
    case: EvaluationCase,
    corpus: SeededEvaluationCorpus,
    *,
    top_k: int = 5,
    max_distance: float | None = None,
) -> RetrievalObservation:
    try:
        owner_id = corpus.owner_ids[
            case.owner_key
        ]
    except KeyError as exc:
        raise ValueError(
            "Evaluation case references "
            f"unknown owner {case.owner_key!r}."
        ) from exc

    results = search_chunks_hybrid(
        session=session,
        query=case.question,
        top_k=top_k,
        owner_id=owner_id,
        max_distance=max_distance,
    )

    document_keys: list[str] = []
    seen_document_keys: set[str] = set()

    for result in results:
        document_id = result.document.id

        if document_id is None:
            raise RuntimeError(
                "Retrieved document does not "
                "have a persisted ID."
            )

        try:
            document_key = (
                corpus.document_keys_by_id[
                    document_id
                ]
            )
        except KeyError as exc:
            raise RuntimeError(
                "Retrieved document is outside "
                "the seeded evaluation corpus."
            ) from exc

        if document_key in seen_document_keys:
            continue

        seen_document_keys.add(document_key)
        document_keys.append(document_key)

    return RetrievalObservation(
        document_keys=tuple(document_keys),
        results=tuple(results),
    )


def cleanup_evaluation_corpus(
    session: Session,
    corpus: SeededEvaluationCorpus,
) -> None:
    if corpus.document_ids:
        session.exec(
            delete(Chunk).where(
                Chunk.document_id.in_(
                    corpus.document_ids
                )
            )
        )

        session.exec(
            delete(Document).where(
                Document.id.in_(
                    corpus.document_ids
                )
            )
        )

    if corpus.user_ids:
        session.exec(
            delete(User).where(
                User.id.in_(
                    corpus.user_ids
                )
            )
        )

    session.commit()