from evaluation.layered import (
    EvaluationLayer,
    LayerEvaluationChecks,
    LayerStatus,
    evaluate_layered_checks,
)


def test_retrieval_failure_blocks_downstream_layers():
    result = evaluate_layered_checks(
        LayerEvaluationChecks(
            retrieval=False,
            context=True,
            answerability=True,
            generation=True,
        )
    )

    assert result.retrieval == LayerStatus.FAIL
    assert result.context == LayerStatus.BLOCKED
    assert result.answerability == LayerStatus.BLOCKED
    assert result.generation == LayerStatus.BLOCKED
    assert result.first_failure == EvaluationLayer.RETRIEVAL


def test_context_failure_is_first_failure_after_retrieval_passes():
    result = evaluate_layered_checks(
        LayerEvaluationChecks(
            retrieval=True,
            context=False,
            answerability=True,
            generation=True,
        )
    )

    assert result.retrieval == LayerStatus.PASS
    assert result.context == LayerStatus.FAIL
    assert result.answerability == LayerStatus.BLOCKED
    assert result.generation == LayerStatus.BLOCKED
    assert result.first_failure == EvaluationLayer.CONTEXT


def test_answerability_failure_blocks_generation():
    result = evaluate_layered_checks(
        LayerEvaluationChecks(
            retrieval=True,
            context=True,
            answerability=False,
            generation=True,
        )
    )

    assert result.retrieval == LayerStatus.PASS
    assert result.context == LayerStatus.PASS
    assert result.answerability == LayerStatus.FAIL
    assert result.generation == LayerStatus.BLOCKED
    assert result.first_failure == EvaluationLayer.ANSWERABILITY


def test_generation_failure_is_reported_after_upstream_layers_pass():
    result = evaluate_layered_checks(
        LayerEvaluationChecks(
            retrieval=True,
            context=True,
            answerability=True,
            generation=False,
        )
    )

    assert result.retrieval == LayerStatus.PASS
    assert result.context == LayerStatus.PASS
    assert result.answerability == LayerStatus.PASS
    assert result.generation == LayerStatus.FAIL
    assert result.first_failure == EvaluationLayer.GENERATION


def test_all_evaluated_layers_can_pass():
    result = evaluate_layered_checks(
        LayerEvaluationChecks(
            retrieval=True,
            context=True,
            answerability=True,
            generation=True,
        )
    )

    assert result.retrieval == LayerStatus.PASS
    assert result.context == LayerStatus.PASS
    assert result.answerability == LayerStatus.PASS
    assert result.generation == LayerStatus.PASS
    assert result.first_failure is None


def test_generation_can_remain_not_evaluated_without_becoming_failure():
    result = evaluate_layered_checks(
        LayerEvaluationChecks(
            retrieval=True,
            context=True,
            answerability=True,
            generation=None,
        )
    )

    assert result.retrieval == LayerStatus.PASS
    assert result.context == LayerStatus.PASS
    assert result.answerability == LayerStatus.PASS
    assert result.generation == LayerStatus.NOT_EVALUATED
    assert result.first_failure is None


def test_missing_context_measurement_keeps_downstream_not_evaluated():
    result = evaluate_layered_checks(
        LayerEvaluationChecks(
            retrieval=True,
            context=None,
            answerability=True,
            generation=True,
        )
    )

    assert result.retrieval == LayerStatus.PASS
    assert result.context == LayerStatus.NOT_EVALUATED
    assert result.answerability == LayerStatus.NOT_EVALUATED
    assert result.generation == LayerStatus.NOT_EVALUATED
    assert result.first_failure is None