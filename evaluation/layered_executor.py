from dataclasses import dataclass

from app.services.context_builder import (
    RagContext,
    build_rag_context,
)
from app.services.semantic_answerability import (
    SemanticAnswerabilityEvaluator,
)
from evaluation.answerability_evaluation import (
    AnswerabilityEvaluationResult,
    evaluate_answerability_case,
)
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


@dataclass(frozen=True)
class ContextEvaluationResult:
    evidence_count: int
    has_text: bool
    evidence_preserved: bool
    content_preserved: bool
    text_presence_matches: bool
    passed: bool


@dataclass(frozen=True)
class LayeredCaseEvaluationResult:
    retrieval: RetrievalEvaluationResult
    context: ContextEvaluationResult
    answerability: AnswerabilityEvaluationResult | None
    layered: LayeredEvaluationResult


def evaluate_context_layer(
    observation: RetrievalObservation,
    context: RagContext,
) -> ContextEvaluationResult:
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


def evaluate_layered_case(
    case: EvaluationCase,
    observation: RetrievalObservation,
    evaluator: SemanticAnswerabilityEvaluator | None = None,
) -> LayeredCaseEvaluationResult:
    retrieval_result = evaluate_retrieval_case(
        case=case,
        observation=observation,
    )

    context = build_rag_context(
        observation.results
    )

    context_result = evaluate_context_layer(
        observation=observation,
        context=context,
    )

    upstream_failed = (
        retrieval_result.passed is False
        or context_result.passed is False
    )

    if upstream_failed:
        answerability_result = None
        answerability_check = None
    else:
        answerability_result = (
            evaluate_answerability_case(
                case=case,
                context=context,
                evaluator=evaluator,
            )
        )

        answerability_check = (
            answerability_result.passed
        )

    layered_result = evaluate_layered_checks(
        LayerEvaluationChecks(
            retrieval=retrieval_result.passed,
            context=context_result.passed,
            answerability=answerability_check,
            generation=None,
        )
    )

    return LayeredCaseEvaluationResult(
        retrieval=retrieval_result,
        context=context_result,
        answerability=answerability_result,
        layered=layered_result,
    )