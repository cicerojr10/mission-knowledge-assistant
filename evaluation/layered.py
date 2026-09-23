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
    checks_by_layer = (
        (
            EvaluationLayer.RETRIEVAL,
            checks.retrieval,
        ),
        (
            EvaluationLayer.CONTEXT,
            checks.context,
        ),
        (
            EvaluationLayer.ANSWERABILITY,
            checks.answerability,
        ),
        (
            EvaluationLayer.GENERATION,
            checks.generation,
        ),
    )

    statuses: dict[
        EvaluationLayer,
        LayerStatus,
    ] = {}

    first_failure: EvaluationLayer | None = None
    blocked = False

    for layer, check in checks_by_layer:
        if blocked:
            statuses[layer] = LayerStatus.BLOCKED
            continue

        if check is None:
            statuses[layer] = (
                LayerStatus.NOT_EVALUATED
            )
            continue

        if check is False:
            statuses[layer] = LayerStatus.FAIL
            first_failure = layer
            blocked = True
            continue

        statuses[layer] = LayerStatus.PASS

    return LayeredEvaluationResult(
        retrieval=statuses[
            EvaluationLayer.RETRIEVAL
        ],
        context=statuses[
            EvaluationLayer.CONTEXT
        ],
        answerability=statuses[
            EvaluationLayer.ANSWERABILITY
        ],
        generation=statuses[
            EvaluationLayer.GENERATION
        ],
        first_failure=first_failure,
    )