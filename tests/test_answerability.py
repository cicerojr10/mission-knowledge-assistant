from types import SimpleNamespace

from app.services.answerability import assess_answerability
from app.services.context_builder import RagContext


def test_answerability_abstains_without_context():
    context = RagContext(
        text="",
        evidence=(),
    )

    decision = assess_answerability(context)

    assert decision.should_abstain is True
    assert decision.can_generate is False
    assert decision.reason == "no_context"


def test_answerability_requires_semantic_evaluation_with_context():
    context = RagContext(
        text="Authorized evidence.",
        evidence=(SimpleNamespace(),),
    )

    decision = assess_answerability(context)

    assert decision.should_abstain is False
    assert decision.can_generate is False
    assert decision.reason == "semantic_evaluation_required"
