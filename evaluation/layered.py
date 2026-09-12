from dataclasses import dataclass
from enum import StrEnum


class EvaluationLayer(StrEnum):
    RETRIEVAL = "retrieval"
    CONTEXT = "context"
    ANSWERABILITY = "answerability"
    GENERATION = "generation"


class LayerStatus(StrEnum):
    PASS = "pass"
    FAIL = "fail"
    BLOCKED = "blocked"
    NOT_EVALUATED = "not_evaluated"


@dataclass(frozen=True)
class LayerEvaluationChecks:
    retrieval: bool | None
    context: bool | None
    answerability: bool | None
    generation: bool | None


@dataclass(frozen=True)
class LayeredEvaluationResult:
    retrieval: LayerStatus
    context: LayerStatus
    answerability: LayerStatus
    generation: LayerStatus
    first_failure: EvaluationLayer | None


def evaluate_layered_checks(
    checks: LayerEvaluationChecks,
) -> LayeredEvaluationResult:
    if checks.retrieval is None:
        return LayeredEvaluationResult(
            retrieval=LayerStatus.NOT_EVALUATED,
            context=LayerStatus.NOT_EVALUATED,
            answerability=LayerStatus.NOT_EVALUATED,
            generation=LayerStatus.NOT_EVALUATED,
            first_failure=None,
        )

    if checks.retrieval is False:
        return LayeredEvaluationResult(
            retrieval=LayerStatus.FAIL,
            context=LayerStatus.BLOCKED,
            answerability=LayerStatus.BLOCKED,
            generation=LayerStatus.BLOCKED,
            first_failure=EvaluationLayer.RETRIEVAL,
        )

    if checks.context is None:
        return LayeredEvaluationResult(
            retrieval=LayerStatus.PASS,
            context=LayerStatus.NOT_EVALUATED,
            answerability=LayerStatus.NOT_EVALUATED,
            generation=LayerStatus.NOT_EVALUATED,
            first_failure=None,
        )

    if checks.context is False:
        return LayeredEvaluationResult(
            retrieval=LayerStatus.PASS,
            context=LayerStatus.FAIL,
            answerability=LayerStatus.BLOCKED,
            generation=LayerStatus.BLOCKED,
            first_failure=EvaluationLayer.CONTEXT,
        )

    if checks.answerability is None:
        return LayeredEvaluationResult(
            retrieval=LayerStatus.PASS,
            context=LayerStatus.PASS,
            answerability=LayerStatus.NOT_EVALUATED,
            generation=LayerStatus.NOT_EVALUATED,
            first_failure=None,
        )

    if checks.answerability is False:
        return LayeredEvaluationResult(
            retrieval=LayerStatus.PASS,
            context=LayerStatus.PASS,
            answerability=LayerStatus.FAIL,
            generation=LayerStatus.BLOCKED,
            first_failure=EvaluationLayer.ANSWERABILITY,
        )

    if checks.generation is None:
        return LayeredEvaluationResult(
            retrieval=LayerStatus.PASS,
            context=LayerStatus.PASS,
            answerability=LayerStatus.PASS,
            generation=LayerStatus.NOT_EVALUATED,
            first_failure=None,
        )

    if checks.generation is False:
        return LayeredEvaluationResult(
            retrieval=LayerStatus.PASS,
            context=LayerStatus.PASS,
            answerability=LayerStatus.PASS,
            generation=LayerStatus.FAIL,
            first_failure=EvaluationLayer.GENERATION,
        )

    return LayeredEvaluationResult(
        retrieval=LayerStatus.PASS,
        context=LayerStatus.PASS,
        answerability=LayerStatus.PASS,
        generation=LayerStatus.PASS,
        first_failure=None,
    )