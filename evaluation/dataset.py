import json
from pathlib import Path

from evaluation.models import (
    EvaluationCase,
    EvaluationCategory,
)


def load_evaluation_cases(
    path: Path,
) -> list[EvaluationCase]:
    cases: list[EvaluationCase] = []

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
                case = EvaluationCase(
                    id=data["id"],
                    category=EvaluationCategory(
                        data["category"]
                    ),
                    question=data["question"],
                    expected_abstained=data[
                        "expected_abstained"
                    ],
                    expected_document_keys=tuple(
                        data.get(
                            "expected_document_keys",
                            [],
                        )
                    ),
                    forbidden_document_keys=tuple(
                        data.get(
                            "forbidden_document_keys",
                            [],
                        )
                    ),
                    reference_answer=data.get(
                        "reference_answer"
                    ),
                )
            except (
                KeyError,
                TypeError,
                ValueError,
            ) as exc:
                raise ValueError(
                    "Invalid evaluation case "
                    f"at line {line_number}."
                ) from exc

            cases.append(case)

    return cases