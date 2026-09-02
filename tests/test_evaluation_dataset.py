from pathlib import Path
from tempfile import TemporaryDirectory

import pytest

from evaluation.dataset import load_evaluation_cases
from evaluation.models import EvaluationCategory


def test_load_evaluation_cases():
    with TemporaryDirectory(
        dir=Path(__file__).resolve().parent
    ) as temp_dir:
        dataset_path = (
            Path(temp_dir) / "cases.jsonl"
        )

        dataset_path.write_text(
            "\n".join(
                [
                    (
                        '{"id":"case-001",'
                        '"category":"answerable",'
                        '"question":"What does the document say?",'
                        '"expected_abstained":false,'
                        '"expected_document_keys":["doc-a"],'
                        '"forbidden_document_keys":[],'
                        '"reference_answer":"Expected answer."}'
                    ),
                    (
                        '{"id":"case-002",'
                        '"category":"unanswerable",'
                        '"question":"What is not documented?",'
                        '"expected_abstained":true,'
                        '"expected_document_keys":[],'
                        '"forbidden_document_keys":[]}'
                    ),
                ]
            ),
            encoding="utf-8",
        )

        cases = load_evaluation_cases(
            dataset_path
        )

    assert len(cases) == 2

    first_case = cases[0]

    assert first_case.id == "case-001"
    assert (
        first_case.category
        == EvaluationCategory.ANSWERABLE
    )
    assert first_case.expected_abstained is False
    assert first_case.expected_document_keys == (
        "doc-a",
    )
    assert first_case.forbidden_document_keys == ()
    assert (
        first_case.reference_answer
        == "Expected answer."
    )

    second_case = cases[1]

    assert (
        second_case.category
        == EvaluationCategory.UNANSWERABLE
    )
    assert second_case.expected_abstained is True
    assert second_case.reference_answer is None


def test_load_evaluation_cases_reports_invalid_line():
    with TemporaryDirectory(
        dir=Path(__file__).resolve().parent
    ) as temp_dir:
        dataset_path = (
            Path(temp_dir) / "cases.jsonl"
        )

        dataset_path.write_text(
            (
                '{"id":"case-001",'
                '"category":"invalid-category",'
                '"question":"Question?",'
                '"expected_abstained":false}'
            ),
            encoding="utf-8",
        )

        with pytest.raises(
            ValueError,
            match="Invalid evaluation case at line 1.",
        ):
            load_evaluation_cases(
                dataset_path
            )