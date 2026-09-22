from types import SimpleNamespace

import evaluation.layered_executor as layered_executor
from app.services.answerability import (
    AnswerabilityDecision,
)
from app.services.context_builder import RagContext
from app.services.semantic_answerability import (
    SemanticAnswerabilityRequest,
)
from evaluation.layered import (
    EvaluationLayer,
    LayerStatus,
)
from evaluation.layered_executor import (
    evaluate_layered_case,
)
from evaluation.models import (
    EvaluationCase,
    EvaluationCategory,
)
from evaluation.retrieval_executor import (
    RetrievalObservation,
)


class FakeSemanticEvaluator:
    def __init__(
        self,
        decision: AnswerabilityDecision,
    ):
        self.decision = decision
        self.received_request = None

    def evaluate(
        self,
        request: SemanticAnswerabilityRequest,
    ) -> AnswerabilityDecision:
        self.received_request = request
        return self.decision


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


def test_retrieval_and_context_pass_without_semantic_evaluator():
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

    result = evaluate_layered_case(
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

    assert result.answerability is not None
    assert result.answerability.evaluated is False
    assert result.answerability.passed is None
    assert (
        result.answerability.reason
        == "semantic_evaluation_required"
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


def test_retrieval_failure_blocks_downstream_layers():
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

    result = evaluate_layered_case(
        case=create_answerable_case(),
        observation=observation,
    )

    assert result.retrieval.passed is False

    # O Context Builder funcionou estruturalmente.
    assert result.context.passed is True

    # Answerability não deve ser executada depois
    # de uma falha causal anterior.
    assert result.answerability is None

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


def test_context_failure_blocks_answerability(
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

    result = evaluate_layered_case(
        case=create_answerable_case(),
        observation=observation,
    )

    assert result.retrieval.passed is True
    assert result.context.passed is False
    assert result.answerability is None

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


def test_unscored_retrieval_does_not_block_answerability():
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

    result = evaluate_layered_case(
        case=case,
        observation=observation,
    )

    assert result.retrieval.scored is False
    assert result.retrieval.passed is None

    assert result.context.passed is True

    assert result.answerability is not None
    assert result.answerability.evaluated is False
    assert result.answerability.passed is None

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


def test_no_context_abstention_passes_answerability_layer():
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
        document_keys=(),
        results=(),
    )

    result = evaluate_layered_case(
        case=case,
        observation=observation,
    )

    assert result.retrieval.passed is None
    assert result.context.passed is True

    assert result.answerability is not None
    assert result.answerability.evaluated is True
    assert result.answerability.passed is True
    assert (
        result.answerability.observed_abstained
        is True
    )
    assert result.answerability.reason == "no_context"

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
        == LayerStatus.PASS
    )
    assert (
        result.layered.generation
        == LayerStatus.NOT_EVALUATED
    )
    assert result.layered.first_failure is None


def test_controlled_semantic_allow_passes_answerability_layer():
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

    evaluator = FakeSemanticEvaluator(
        AnswerabilityDecision(
            should_abstain=False,
            can_generate=True,
            reason="semantic_evaluation_passed",
        )
    )

    result = evaluate_layered_case(
        case=create_answerable_case(),
        observation=observation,
        evaluator=evaluator,
    )

    assert result.answerability is not None
    assert result.answerability.evaluated is True
    assert result.answerability.passed is True
    assert (
        result.answerability.semantic_evaluation_used
        is True
    )

    assert evaluator.received_request is not None
    assert (
        evaluator.received_request.question
        == "What is the expected fact?"
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
        == LayerStatus.PASS
    )
    assert (
        result.layered.generation
        == LayerStatus.NOT_EVALUATED
    )
    assert result.layered.first_failure is None


def test_controlled_semantic_mismatch_is_answerability_failure():
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

    evaluator = FakeSemanticEvaluator(
        AnswerabilityDecision(
            should_abstain=True,
            can_generate=False,
            reason="insufficient_semantic_evidence",
        )
    )

    result = evaluate_layered_case(
        case=create_answerable_case(),
        observation=observation,
        evaluator=evaluator,
    )

    assert result.answerability is not None
    assert result.answerability.evaluated is True
    assert result.answerability.passed is False

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
        == LayerStatus.FAIL
    )
    assert (
        result.layered.generation
        == LayerStatus.BLOCKED
    )
    assert (
        result.layered.first_failure
        == EvaluationLayer.ANSWERABILITY
    )