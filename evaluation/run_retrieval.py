import argparse
from pathlib import Path

from sqlmodel import Session

from app.database import engine
from evaluation.corpus import (
    load_evaluation_documents,
)
from evaluation.dataset import load_evaluation_cases
from evaluation.retrieval_executor import (
    SeededEvaluationCorpus,
    cleanup_evaluation_corpus,
    execute_retrieval_case,
    seed_evaluation_corpus,
)
from evaluation.retrieval_metrics import (
    evaluate_retrieval_case,
    summarize_retrieval_results,
)


DATA_DIRECTORY = (
    Path(__file__).resolve().parent
    / "data"
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Run the MKA retrieval evaluation "
            "against PostgreSQL and real embeddings."
        )
    )

    parser.add_argument(
        "--top-k",
        type=int,
        default=1,
        help=(
            "Maximum number of hybrid retrieval "
            "results. Default: 1."
        ),
    )

    parser.add_argument(
        "--max-distance",
        type=float,
        default=None,
        help=(
            "Optional maximum semantic cosine "
            "distance."
        ),
    )

    return parser.parse_args()


def format_rate(value: float) -> str:
    return f"{value * 100:.2f}%"


def main() -> None:
    args = parse_args()

    if args.top_k < 1:
        raise ValueError(
            "top_k must be at least 1."
        )

    documents = load_evaluation_documents(
        DATA_DIRECTORY / "corpus.jsonl"
    )

    cases = load_evaluation_cases(
        DATA_DIRECTORY / "cases.jsonl"
    )

    with Session(engine) as session:
        corpus: SeededEvaluationCorpus | None = None

        try:
            corpus = seed_evaluation_corpus(
                session=session,
                documents=documents,
            )

            results = []

            for case in cases:
                observation = execute_retrieval_case(
                    session=session,
                    case=case,
                    corpus=corpus,
                    top_k=args.top_k,
                    max_distance=args.max_distance,
                )

                result = evaluate_retrieval_case(
                    case=case,
                    observation=observation,
                )

                results.append(result)

            summary = summarize_retrieval_results(
                results
            )

            print()
            print("MKA RETRIEVAL EVALUATION")
            print("========================")
            print(
                f"top_k: {args.top_k}"
            )
            print(
                "max_distance: "
                f"{args.max_distance}"
            )
            print()

            for result in results:
                if result.passed is True:
                    status = "PASS"
                elif result.passed is False:
                    status = "FAIL"
                else:
                    status = "INFO"

                retrieved = (
                    ", ".join(
                        result.document_keys
                    )
                    or "-"
                )

                print(
                    f"[{status}] "
                    f"{result.case_id} "
                    f"({result.category.value}) "
                    f"retrieved=[{retrieved}]"
                )

                if (
                    result.first_expected_rank
                    is not None
                ):
                    print(
                        "       "
                        "first_expected_rank="
                        f"{result.first_expected_rank}"
                    )

            print()
            print("SUMMARY")
            print("-------")
            print(
                "total_cases: "
                f"{summary.total_cases}"
            )
            print(
                "scored_cases: "
                f"{summary.scored_cases}"
            )
            print(
                "scored_pass_rate: "
                f"{format_rate(summary.scored_pass_rate)}"
            )
            print(
                f"expected_case_hit@{args.top_k}: "
                f"{format_rate(summary.expected_case_hit_rate)}"
            )
            print(
                f"expected_document_recall@{args.top_k}: "
                f"{format_rate(summary.expected_document_recall)}"
            )
            print(
                "forbidden_document_absence: "
                f"{format_rate(summary.forbidden_document_absence_rate)}"
            )

        finally:
            if corpus is not None:
                cleanup_evaluation_corpus(
                    session=session,
                    corpus=corpus,
                )


if __name__ == "__main__":
    main()
