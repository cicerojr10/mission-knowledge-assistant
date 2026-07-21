from fastapi.testclient import TestClient
from sqlmodel import Session, select

from app.database import engine
from app.main import app
from app.models import Chunk, Document
from app.services.embeddings import generate_embedding


EVALUATION_TITLE_PREFIX = "[DAY7-EVAL]"

TARGET_TITLE = (
    f"{EVALUATION_TITLE_PREFIX} "
    "Hybrid Search Verification"
)

TARGET_CONTENT = (
    "Day seven hybrid search verification"
)

UNRELATED_TITLE = (
    f"{EVALUATION_TITLE_PREFIX} "
    "Unrelated Database Document"
)

UNRELATED_CONTENT = (
    "PostgreSQL stores structured data "
    "for backend applications."
)


client = TestClient(app)


def delete_evaluation_corpus(
    session: Session,
) -> int:
    """
    Remove somente os documentos temporários do Dia 7.
    """
    statement = select(Document).where(
        Document.title.startswith(
            EVALUATION_TITLE_PREFIX
        )
    )

    documents = session.exec(statement).all()

    for document in documents:
        session.delete(document)

    session.commit()

    return len(documents)


def create_document_with_embedding(
    session: Session,
    *,
    title: str,
    content: str,
) -> Document:
    """
    Cria um documento com um chunk e embedding real.
    """
    document = Document(
        title=title,
        content=content,
    )

    session.add(document)
    session.flush()

    if document.id is None:
        raise RuntimeError(
            "Document ID was not generated."
        )

    embedding = generate_embedding(content)

    chunk = Chunk(
        document_id=document.id,
        content=content,
        chunk_index=0,
        char_count=len(content),
        embedding=embedding,
    )

    session.add(chunk)
    session.commit()
    session.refresh(document)

    return document


def run_hybrid_search_validation() -> None:
    """
    Executa a rota híbrida com modelo e banco reais.
    """
    response = client.get(
        "/search/hybrid",
        params={
            "q": TARGET_CONTENT,
            "top_k": 3,
            "max_distance": 0.60,
            "rrf_k": 60,
        },
    )

    print(f"status_code={response.status_code}")

    if response.status_code != 200:
        raise RuntimeError(
            f"Hybrid search failed: {response.text}"
        )

    results = response.json()

    print(f"result_count={len(results)}")

    for position, result in enumerate(
        results,
        start=1,
    ):
        print(
            f"position={position} | "
            f"title={result['document_title']} | "
            f"rrf_score={result['rrf_score']:.8f} | "
            f"textual_rank={result['textual_rank']} | "
            f"semantic_rank={result['semantic_rank']} | "
            f"semantic_distance="
            f"{result['semantic_distance']}"
        )

    if not results:
        raise RuntimeError(
            "Hybrid search returned no results."
        )

    first_result = results[0]

    if first_result["document_title"] != TARGET_TITLE:
        raise RuntimeError(
            "Expected evaluation document was not "
            "ranked first."
        )

    if first_result["textual_rank"] != 1:
        raise RuntimeError(
            "Expected textual rank 1."
        )

    if first_result["semantic_rank"] != 1:
        raise RuntimeError(
            "Expected semantic rank 1."
        )

    print("hybrid_validation=PASS")


def main() -> None:
    with Session(engine) as session:
        removed_before = delete_evaluation_corpus(
            session
        )

        print(
            "stale_evaluation_documents_removed="
            f"{removed_before}"
        )

        try:
            create_document_with_embedding(
                session,
                title=TARGET_TITLE,
                content=TARGET_CONTENT,
            )

            create_document_with_embedding(
                session,
                title=UNRELATED_TITLE,
                content=UNRELATED_CONTENT,
            )

            print(
                "evaluation_documents_created=2"
            )

            run_hybrid_search_validation()

        finally:
            removed_after = delete_evaluation_corpus(
                session
            )

            print(
                "evaluation_documents_removed_after_run="
                f"{removed_after}"
            )


if __name__ == "__main__":
    main()