from types import SimpleNamespace

from app.services.context_builder import build_rag_context


def test_build_rag_context_preserves_evidence_and_order():
    first_result = SimpleNamespace(
        chunk=SimpleNamespace(
            id=101,
            content="First authorized fact.",
            chunk_index=0,
        ),
        document=SimpleNamespace(
            id=201,
            title="First document",
        ),
    )

    second_result = SimpleNamespace(
        chunk=SimpleNamespace(
            id=102,
            content="Second authorized fact.",
            chunk_index=1,
        ),
        document=SimpleNamespace(
            id=202,
            title="Second document",
        ),
    )

    context = build_rag_context(
        [first_result, second_result]
    )

    assert context.evidence == (
        first_result,
        second_result,
    )

    assert context.text == (
        "[Source 1]\n"
        "Document: First document\n"
        "Document ID: 201\n"
        "Chunk ID: 101\n"
        "Chunk index: 0\n"
        "Content:\n"
        "First authorized fact.\n\n"
        "[Source 2]\n"
        "Document: Second document\n"
        "Document ID: 202\n"
        "Chunk ID: 102\n"
        "Chunk index: 1\n"
        "Content:\n"
        "Second authorized fact."
    )


def test_build_rag_context_returns_empty_context_without_evidence():
    context = build_rag_context([])

    assert context.text == ""
    assert context.evidence == ()
