import argparse
from pathlib import Path

from sqlmodel import Session

from app.database import engine
from evaluation.corpus import (
    load_evaluation_documents,
)
from evaluation.dataset import load_evaluation_cases
from evaluation.layered import EvaluationLayer
from evaluation.layered_executor import (
    LayeredCaseEvaluationResult,
    evaluate_layered_case,
)
from evaluation.layered_metrics import (
    LayerStatusSummary,
    summarize_layered_results,
)
from evaluation.retrieval_executor import (
    SeededEvaluationCorpus,
    cleanup_evaluation_corpus,
    execute_retrieval_case,
    seed_evaluation_corpus,
)
from evaluation.retrieval_metrics import (
    summarize_retrieval_results,
)


DATA_DIRECTORY = (
    Path(__file__).resolve().parent
    / "data"
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Run the MKA layered evaluation "
            "against real retrieval and context."
        )
    )

    parser.add_argument(
        "--top-k",
        type=int,
        default=5,
        help=(
            "Maximum number of hybrid retrieval "
            "results. Default: 5."
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


def print_layer_summary(
    name: str,
    summary: LayerStatusSummary,
) -> None:
    if summary.evaluated_cases == 0:
        pass_rate = "N/A"
    else:
        pass_rate = format_rate(
            summary.pass_rate
        )

    print(name)
    print(
        "  evaluated: "
        f"{summary.evaluated_cases}"
    )
    print(
        "  passed: "
        f"{summary.passed_cases}"
    )
    print(
        "  failed: "
        f"{summary.failed_cases}"
    )
    print(
        "  blocked: "
        f"{summary.blocked_cases}"
    )
    print(
        "  not_evaluated: "
        f"{summary.not_evaluated_cases}"
    )
    print(
        "  pass_rate: "
        f"{pass_rate}"
    )


def print_case_result(
    case_id: str,
    category: str,
    result: LayeredCaseEvaluationResult,
) -> None:
    first_failure = (
        result.layered.first_failure.value
        if result.layered.first_failure
        is not None
        else "-"
    )

    print(
        f"{case_id} "
        f"({category}) "
        f"retrieval={result.layered.retrieval.value.upper()} "
        f"context={result.layered.context.value.upper()} "
        "answerability="
        f"{result.layered.answerability.value.upper()} "
        f"generation={result.layered.generation.value.upper()} "
        f"first_failure={first_failure}"
    )


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

            results: list[
                LayeredCaseEvaluationResult
            ] = []

            for case in cases:
                observation = execute_retrieval_case(
                    session=session,
                    case=case,
                    corpus=corpus,
                    top_k=args.top_k,
                    max_distance=args.max_distance,
                )

                result = evaluate_layered_case(
                    case=case,
                    observation=observation,
                )

                results.append(result)

            layered_summary = (
                summarize_layered_results(
                    [
                        result.layered
                        for result in results
                    ]
                )
            )

            retrieval_summary = (
                summarize_retrieval_results(
                    [
                        result.retrieval
                        for result in results
                    ]
                )
            )

            print()
            print("MKA LAYERED EVALUATION")
            print("======================")
            print(
                f"top_k: {args.top_k}"
            )
            print(
                "max_distance: "
                f"{args.max_distance}"
            )
            print(
                "semantic_evaluator: disabled"
            )
            print(
                "generation_evaluation: disabled"
            )
            print()

            print("CASES")
            print("-----")

            for case, result in zip(
                cases,
                results,
                strict=True,
            ):
                print_case_result(
                    case_id=case.id,
                    category=case.category.value,
                    result=result,
                )

            print()
            print("RETRIEVAL SUMMARY")
            print("-----------------")
            print(
                "scored_cases: "
                f"{retrieval_summary.scored_cases}"
            )
            print(
                "scored_pass_rate: "
                f"{format_rate(
                    retrieval_summary.scored_pass_rate
                )}"
            )
            print(
                f"expected_case_hit@{args.top_k}: "
                f"{format_rate(
                    retrieval_summary.expected_case_hit_rate
                )}"
            )
            print(
                f"expected_document_recall@{args.top_k}: "
                f"{format_rate(
                    retrieval_summary.expected_document_recall
                )}"
            )
            print(
                "forbidden_document_absence: "
                f"{format_rate(
                    retrieval_summary.forbidden_document_absence_rate
                )}"
            )

            print()
            print("LAYER SUMMARY")
            print("-------------")

            print_layer_summary(
                "retrieval:",
                layered_summary.retrieval,
            )
            print_layer_summary(
                "context:",
                layered_summary.context,
            )
            print_layer_summary(
                "answerability:",
                layered_summary.answerability,
            )
            print_layer_summary(
                "generation:",
                layered_summary.generation,
            )

            print()
            print("FIRST FAILURE")
            print("-------------")

            for layer in EvaluationLayer:
                print(
                    f"{layer.value}: "
                    f"{layered_summary.first_failure_counts[layer]}"
                )

            print(
                "cases_with_failure: "
                f"{layered_summary.cases_with_failure}"
            )
            print(
                "no_failure_observed_cases: "
                f"{layered_summary.no_failure_observed_cases}"
            )
            print(
                "observed_failure_rate: "
                f"{format_rate(
                    layered_summary.observed_failure_rate
                )}"
            )

        finally:
            if corpus is not None:
                cleanup_evaluation_corpus(
                    session=session,
                    corpus=corpus,
                )


if __name__ == "__main__":
    main()