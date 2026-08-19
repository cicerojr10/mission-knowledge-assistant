from collections.abc import Sequence
from dataclasses import dataclass

from app.services.hybrid_search import HybridSearchResult


@dataclass(frozen=True)
class RagContext:
    text: str
    evidence: tuple[HybridSearchResult, ...]


def build_rag_context(
    results: Sequence[HybridSearchResult],
) -> RagContext:
    evidence = tuple(results)

    sections = []

    for index, result in enumerate(evidence, start=1):
        sections.append(
            "\n".join(
                [
                    f"[Source {index}]",
                    f"Document: {result.document.title}",
                    f"Document ID: {result.document.id}",
                    f"Chunk ID: {result.chunk.id}",
                    f"Chunk index: {result.chunk.chunk_index}",
                    "Content:",
                    result.chunk.content,
                ]
            )
        )

    return RagContext(
        text="\n\n".join(sections),
        evidence=evidence,
    )
