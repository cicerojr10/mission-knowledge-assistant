from types import SimpleNamespace

import evaluation.layered_executor as layered_executor
from app.services.context_builder import RagContext
from evaluation.layered import (
    EvaluationLayer,
    LayerStatus,
)
from evaluation.layered_executor import (
    evaluate_retrieval_context_case,
)
from evaluation.models import (
    EvaluationCase,
    EvaluationCategory,
)
from evaluation.retrieval_executor import (
    RetrievalObservation,
)


def create_result(
    document_id: int,
    document_title: str,
    chunk_id: int,
    content: str,
):
    return SimpleNamespace(
        document=SimpleNamespace(
            id=document_id,
            title=document_title,
        ),
        chunk=SimpleNamespace(
            id=chunk_id,
            content=content,
            chunk_index=0,
        ),
    )


def create_answerable_case():
    return EvaluationCase(
        id="case-001",
        category=EvaluationCategory.ANSWERABLE,
        owner_key="primary",
        question="What is the expected fact?",
        expected_abstained=False,
        expected_document_keys=("doc-a",),
        forbidden_document_keys=(),
    )


def test_retrieval_and_context_layers_pass_together():
    result_a = create_result(
        document_id=100,
        document_title="Document A",
        chunk_id=1000,
        content="Expected fact.",
    )

    observation = RetrievalObservation(
        document_keys=("doc-a",),
        results=(result_a,),
    )

    result = evaluate_retrieval_context_case(
        case=create_answerable_case(),
        observation=observation,
    )

    assert result.retrieval.passed is True

    assert result.context.passed is True
    assert result.context.evidence_count == 1
    assert result.context.has_text is True
    assert result.context.evidence_preserved is True
    assert result.context.content_preserved is True
    assert (
        result.context.text_presence_matches
        is True
    )

    assert (
        result.layered.retrieval
        == LayerStatus.PASS
    )
    assert (
        result.layered.context
        == LayerStatus.PASS
    )
    assert (
        result.layered.answerability
        == LayerStatus.NOT_EVALUATED
    )
    assert (
        result.layered.generation
        == LayerStatus.NOT_EVALUATED
    )
    assert result.layered.first_failure is None


def test_retrieval_failure_blocks_context_in_layered_result():
    result_b = create_result(
        document_id=200,
        document_title="Document B",
        chunk_id=2000,
        content="Different fact.",
    )

    observation = RetrievalObservation(
        document_keys=("doc-b",),
        results=(result_b,),
    )

    result = evaluate_retrieval_context_case(
        case=create_answerable_case(),
        observation=observation,
    )

    assert result.retrieval.passed is False

    # O Context Builder funcionou estruturalmente.
    assert result.context.passed is True

    # Mas a análise causal para na primeira falha.
    assert (
        result.layered.retrieval
        == LayerStatus.FAIL
    )
    assert (
        result.layered.context
        == LayerStatus.BLOCKED
    )
    assert (
        result.layered.answerability
        == LayerStatus.BLOCKED
    )
    assert (
        result.layered.generation
        == LayerStatus.BLOCKED
    )
    assert (
        result.layered.first_failure
        == EvaluationLayer.RETRIEVAL
    )


def test_context_failure_is_classified_after_retrieval_passes(
    monkeypatch,
):
    result_a = create_result(
        document_id=100,
        document_title="Document A",
        chunk_id=1000,
        content="Expected fact.",
    )

    observation = RetrievalObservation(
        document_keys=("doc-a",),
        results=(result_a,),
    )

    monkeypatch.setattr(
        layered_executor,
        "build_rag_context",
        lambda results: RagContext(
            text="",
            evidence=(),
        ),
    )

    result = evaluate_retrieval_context_case(
        case=create_answerable_case(),
        observation=observation,
    )

    assert result.retrieval.passed is True
    assert result.context.passed is False

    assert (
        result.layered.retrieval
        == LayerStatus.PASS
    )
    assert (
        result.layered.context
        == LayerStatus.FAIL
    )
    assert (
        result.layered.answerability
        == LayerStatus.BLOCKED
    )
    assert (
        result.layered.generation
        == LayerStatus.BLOCKED
    )
    assert (
        result.layered.first_failure
        == EvaluationLayer.CONTEXT
    )


def test_unscored_retrieval_keeps_layered_result_not_evaluated():
    result_a = create_result(
        document_id=100,
        document_title="Document A",
        chunk_id=1000,
        content="Nearest authorized fact.",
    )

    case = EvaluationCase(
        id="case-unanswerable",
        category=EvaluationCategory.UNANSWERABLE,
        owner_key="primary",
        question="Unknown production fact?",
        expected_abstained=True,
        expected_document_keys=(),
        forbidden_document_keys=(),
    )

    observation = RetrievalObservation(
        document_keys=("doc-a",),
        results=(result_a,),
    )

    result = evaluate_retrieval_context_case(
        case=case,
        observation=observation,
    )

    assert result.retrieval.scored is False
    assert result.retrieval.passed is None

    assert result.context.passed is True

    assert (
        result.layered.retrieval
        == LayerStatus.NOT_EVALUATED
    )
    assert (
    result.layered.context
    == LayerStatus.PASS
    )
    assert (
        result.layered.answerability
        == LayerStatus.NOT_EVALUATED
    )
    assert (
        result.layered.generation
        == LayerStatus.NOT_EVALUATED
    )
    assert result.layered.first_failure is None