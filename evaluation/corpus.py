import json
from pathlib import Path

from evaluation.models import EvaluationDocument


def load_evaluation_documents(
    path: Path,
) -> list[EvaluationDocument]:
    documents: list[EvaluationDocument] = []

    with path.open(
        mode="r",
        encoding="utf-8",
    ) as file:
        for line_number, raw_line in enumerate(
            file,
            start=1,
        ):
            line = raw_line.strip()

            if not line:
                continue

            data = json.loads(line)

            try:
                document = EvaluationDocument(
                    key=data["key"],
                    owner_key=data["owner_key"],
                    title=data["title"],
                    content=data["content"],
                )
            except (
                KeyError,
                TypeError,
            ) as exc:
                raise ValueError(
                    "Invalid evaluation document "
                    f"at line {line_number}."
                ) from exc

            documents.append(document)

    return documents
