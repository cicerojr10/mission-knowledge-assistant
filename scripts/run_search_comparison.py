from sqlmodel import Session, select

from app.database import engine
from app.models import Chunk, Document
from app.services.embeddings import generate_embedding
from scripts.search_comparison_cases import CASES, DOCUMENTS


EVALUATION_TITLE_PREFIX = "[DAY6-EVAL]"
EVALUATION_THRESHOLDS = (
    0.40,
    0.60,
    0.80,
)
EVALUATION_TOP_K_VALUES = (
    1,
    3,
    5,
)

def delete_evaluation_corpus(session: Session) -> int:
    """
    Remove somente os documentos pertencentes ao corpus
    controlado do Dia 6.

    Os chunks relacionados também são removidos por causa
    da configuração de cascade presente nos modelos.
    """
    statement = select(Document).where(
        Document.title.startswith(EVALUATION_TITLE_PREFIX)
    )

    documents = session.exec(statement).all()

    for document in documents:
        session.delete(document)

    session.commit()

    return len(documents)


def create_evaluation_corpus(
    session: Session,
) -> list[Document]:
    """
    Cria um documento e um chunk para cada item do corpus.

    Cada chunk recebe um embedding produzido pelo mesmo
    serviço utilizado pela aplicação.
    """
    created_documents: list[Document] = []

    for evaluation_document in DOCUMENTS:
        document = Document(
            title=(
                f"{EVALUATION_TITLE_PREFIX} "
                f"{evaluation_document.code} | "
                f"{evaluation_document.title}"
            ),
            content=evaluation_document.content,
        )

        session.add(document)
        session.flush()

        if document.id is None:
            raise RuntimeError(
                "Document ID was not generated."
            )

        embedding = generate_embedding(
            evaluation_document.content
        )

        chunk = Chunk(
            document_id=document.id,
            content=evaluation_document.content,
            chunk_index=0,
            char_count=len(evaluation_document.content),
            embedding=embedding,
        )

        session.add(chunk)
        created_documents.append(document)

    session.commit()

    return created_documents


def get_document_code(document: Document) -> str:
    """
    Extrai o código DOC-XX do título controlado.

    Exemplo:

    [DAY6-EVAL] DOC-01 | Artemis Program
    →
    DOC-01
    """
    title_without_prefix = document.title.removeprefix(
        f"{EVALUATION_TITLE_PREFIX} "
    )

    return title_without_prefix.split(
        " | ",
        maxsplit=1,
    )[0]


def search_evaluation_corpus_textually(
    session: Session,
    query: str,
) -> list[tuple[Chunk, Document]]:
    """
    Executa a mesma estratégia lexical utilizada pela
    rota textual da aplicação.

    A consulta fica limitada ao corpus controlado do Dia 6.
    """
    statement = (
        select(Chunk, Document)
        .where(Chunk.document_id == Document.id)
        .where(
            Document.title.startswith(
                EVALUATION_TITLE_PREFIX
            )
        )
        .where(
            Chunk.content.ilike(f"%{query}%")
        )
        .order_by(
            Document.id,
            Chunk.chunk_index,
        )
    )

    return list(
        session.exec(statement).all()
    )


def search_evaluation_corpus_semantically(
    session: Session,
    query: str,
    top_k: int,
    max_distance: float | None = None,
) -> list[tuple[Chunk, Document, float]]:
    """
    Executa busca vetorial somente no corpus controlado
    do Dia 6.
    """
    query_embedding = generate_embedding(query)

    distance_expression = (
        Chunk.embedding.cosine_distance(
            query_embedding
        )
    )

    distance = distance_expression.label("distance")

    statement = (
        select(
            Chunk,
            Document,
            distance,
        )
        .where(
            Chunk.document_id == Document.id
        )
        .where(
            Document.title.startswith(
                EVALUATION_TITLE_PREFIX
            )
        )
        .where(
            Chunk.embedding.is_not(None)
        )
    )

    if max_distance is not None:
        statement = statement.where(
            distance_expression <= max_distance
        )

    statement = (
        statement
        .order_by(distance_expression)
        .limit(top_k)
    )

    results = session.exec(statement).all()

    return [
        (
            chunk,
            document,
            float(result_distance),
        )
        for chunk, document, result_distance in results
    ]


def print_baseline_comparison(
    session: Session,
) -> None:
    """
    Compara:

    - busca textual;
    - busca semântica com top_k=5;
    - busca semântica sem max_distance.
    """
    print()
    print("=" * 72)
    print("BASELINE COMPARISON")
    print("semantic_top_k=5")
    print("semantic_max_distance=None")
    print("=" * 72)

    for evaluation_case in CASES:
        expected = (
            evaluation_case.expected_document_code
            or "NONE"
        )

        textual_results = (
            search_evaluation_corpus_textually(
                session=session,
                query=evaluation_case.query,
            )
        )

        semantic_results = (
            search_evaluation_corpus_semantically(
                session=session,
                query=evaluation_case.query,
                top_k=5,
                max_distance=None,
            )
        )

        textual_codes = [
            get_document_code(document)
            for _, document in textual_results
        ]

        semantic_codes = [
            (
                get_document_code(document),
                round(distance, 4),
            )
            for _, document, distance
            in semantic_results
        ]

        print()
        print(
            f"{evaluation_case.code} | "
            f"category={evaluation_case.category}"
        )

        print(
            f"query={evaluation_case.query}"
        )

        print(
            f"expected={expected}"
        )

        print(
            f"textual={textual_codes}"
        )

        print(
            f"semantic={semantic_codes}"
        )
def print_threshold_comparison(
    session: Session,
) -> None:
    """
    Compara diferentes limites de distância.

    Para casos com documento esperado:
    - PASS: documento esperado foi recuperado;
    - FALSE_NEGATIVE: documento esperado foi descartado.

    Para casos sem documento esperado:
    - PASS: nenhum resultado foi retornado;
    - FALSE_POSITIVE: resultados irrelevantes foram aceitos.
    """
    print()
    print("=" * 72)
    print("THRESHOLD COMPARISON")
    print("semantic_top_k=5")
    print("=" * 72)

    for max_distance in EVALUATION_THRESHOLDS:
        passed = 0
        false_positives = 0
        false_negatives = 0

        print()
        print("-" * 72)
        print(
            f"max_distance={max_distance:.2f}"
        )
        print("-" * 72)

        for evaluation_case in CASES:
            semantic_results = (
                search_evaluation_corpus_semantically(
                    session=session,
                    query=evaluation_case.query,
                    top_k=5,
                    max_distance=max_distance,
                )
            )

            result_codes = [
                get_document_code(document)
                for _, document, _ in semantic_results
            ]

            formatted_results = [
                (
                    get_document_code(document),
                    round(distance, 4),
                )
                for _, document, distance
                in semantic_results
            ]

            expected = (
                evaluation_case.expected_document_code
            )

            if expected is None:
                if result_codes:
                    outcome = "FALSE_POSITIVE"
                    false_positives += 1
                else:
                    outcome = "PASS"
                    passed += 1

                expected_rank = None

            elif expected in result_codes:
                outcome = "PASS"
                passed += 1
                expected_rank = (
                    result_codes.index(expected) + 1
                )

            else:
                outcome = "FALSE_NEGATIVE"
                false_negatives += 1
                expected_rank = None

            expected_label = expected or "NONE"
            rank_label = expected_rank or "-"

            print(
                f"{evaluation_case.code} | "
                f"expected={expected_label} | "
                f"results={formatted_results} | "
                f"rank={rank_label} | "
                f"outcome={outcome}"
            )

        print()
        print(
            f"summary | "
            f"max_distance={max_distance:.2f} | "
            f"passed={passed} | "
            f"false_positives={false_positives} | "
            f"false_negatives={false_negatives}"
        )
        
def print_top_k_comparison(
    session: Session,
) -> None:
    """
    Avalia o efeito de top_k sem aplicar threshold.

    Registra:

    - presença do documento esperado;
    - posição do documento esperado;
    - quantidade total retornada;
    - resultados extras;
    - falsos positivos no caso sem correspondência.
    """
    print()
    print("=" * 72)
    print("TOP_K COMPARISON")
    print("semantic_max_distance=None")
    print("=" * 72)

    for top_k in EVALUATION_TOP_K_VALUES:
        expected_found = 0
        expected_missing = 0
        total_results = 0
        extra_results = 0
        no_match_results = 0

        print()
        print("-" * 72)
        print(f"top_k={top_k}")
        print("-" * 72)

        for evaluation_case in CASES:
            semantic_results = (
                search_evaluation_corpus_semantically(
                    session=session,
                    query=evaluation_case.query,
                    top_k=top_k,
                    max_distance=None,
                )
            )

            result_codes = [
                get_document_code(document)
                for _, document, _ in semantic_results
            ]

            formatted_results = [
                (
                    get_document_code(document),
                    round(distance, 4),
                )
                for _, document, distance
                in semantic_results
            ]

            result_count = len(result_codes)
            total_results += result_count

            expected = (
                evaluation_case.expected_document_code
            )

            if expected is None:
                no_match_results += result_count
                extra_results += result_count

                outcome = (
                    "PASS"
                    if result_count == 0
                    else "FALSE_POSITIVE"
                )

                expected_rank = None

            elif expected in result_codes:
                expected_found += 1

                expected_rank = (
                    result_codes.index(expected) + 1
                )

                extra_results += max(
                    result_count - 1,
                    0,
                )

                outcome = "EXPECTED_FOUND"

            else:
                expected_missing += 1
                extra_results += result_count

                expected_rank = None
                outcome = "EXPECTED_MISSING"

            expected_label = expected or "NONE"
            rank_label = expected_rank or "-"

            print(
                f"{evaluation_case.code} | "
                f"expected={expected_label} | "
                f"results={formatted_results} | "
                f"rank={rank_label} | "
                f"result_count={result_count} | "
                f"outcome={outcome}"
            )

        print()
        print(
            f"summary | "
            f"top_k={top_k} | "
            f"expected_found={expected_found} | "
            f"expected_missing={expected_missing} | "
            f"total_results={total_results} | "
            f"extra_results={extra_results} | "
            f"no_match_results={no_match_results}"
        )

def main() -> None:
    """
    Executa o experimento controlado completo.

    O corpus temporário é apagado antes e depois da execução.
    """
    with Session(engine) as session:
        removed_before = delete_evaluation_corpus(
            session
        )

        print(
            "stale_evaluation_documents_removed="
            f"{removed_before}"
        )

        try:
            documents = create_evaluation_corpus(
                session
            )

            print(
                "evaluation_documents_created="
                f"{len(documents)}"
            )

            for document in documents:
                print(
                    f"id={document.id} | "
                    f"title={document.title}"
                )

            print_baseline_comparison(session)
            print_threshold_comparison(session)
            print_top_k_comparison(session)
        finally:
            removed_after = (
                delete_evaluation_corpus(session)
            )

            print()
            print(
                "evaluation_documents_removed_after_run="
                f"{removed_after}"
            )


if __name__ == "__main__":
    main()