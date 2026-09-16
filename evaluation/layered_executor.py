from dataclasses import dataclass

from evaluation.layered import (
    LayerEvaluationChecks,
    LayeredEvaluationResult,
    evaluate_layered_checks,
)
from evaluation.models import EvaluationCase
from evaluation.retrieval_executor import (
    RetrievalObservation,
)
from evaluation.retrieval_metrics import (
    RetrievalEvaluationResult,
    evaluate_retrieval_case,
)
from app.services.context_builder import (
    build_rag_context,
)


@dataclass(frozen=True)
class ContextEvaluationResult:
    evidence_count: int
    has_text: bool
    evidence_preserved: bool
    content_preserved: bool
    text_presence_matches: bool
    passed: bool


@dataclass(frozen=True)
class RetrievalContextEvaluationResult:
    retrieval: RetrievalEvaluationResult
    context: ContextEvaluationResult
    layered: LayeredEvaluationResult


def evaluate_context_layer(
    observation: RetrievalObservation,
) -> ContextEvaluationResult:
    context = build_rag_context(
        observation.results
    )

    evidence_preserved = (
        context.evidence
        == observation.results
    )

    content_preserved = all(
        result.chunk.content in context.text
        for result in observation.results
    )

    text_presence_matches = (
        bool(context.text)
        is bool(observation.results)
    )

    passed = all(
        (
            evidence_preserved,
            content_preserved,
            text_presence_matches,
        )
    )

    return ContextEvaluationResult(
        evidence_count=len(context.evidence),
        has_text=bool(context.text),
        evidence_preserved=evidence_preserved,
        content_preserved=content_preserved,
        text_presence_matches=(
            text_presence_matches
        ),
        passed=passed,
    )


def evaluate_retrieval_context_case(
    case: EvaluationCase,
    observation: RetrievalObservation,
) -> RetrievalContextEvaluationResult:
    retrieval_result = evaluate_retrieval_case(
        case=case,
        observation=observation,
    )

    context_result = evaluate_context_layer(
        observation
    )

    layered_result = evaluate_layered_checks(
        LayerEvaluationChecks(
            retrieval=retrieval_result.passed,
            context=context_result.passed,
            answerability=None,
            generation=None,
        )
    )

    return RetrievalContextEvaluationResult(
        retrieval=retrieval_result,
        context=context_result,
        layered=layered_result,
    )