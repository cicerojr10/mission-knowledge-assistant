from collections import Counter
from pathlib import Path

from evaluation.corpus import (
    load_evaluation_documents,
)
from evaluation.dataset import load_evaluation_cases
from evaluation.models import EvaluationCategory


DATA_DIRECTORY = (
    Path(__file__).resolve().parents[1]
    / "evaluation"
    / "data"
)


def test_evaluation_dataset_has_expected_shape():
    documents = load_evaluation_documents(
        DATA_DIRECTORY / "corpus.jsonl"
    )
    cases = load_evaluation_cases(
        DATA_DIRECTORY / "cases.jsonl"
    )

    assert len(documents) == 18
    assert len(cases) == 50

    categories = Counter(
        case.category
        for case in cases
    )

    assert categories == {
        EvaluationCategory.ANSWERABLE: 20,
        EvaluationCategory.UNANSWERABLE: 13,
        EvaluationCategory.CROSS_USER: 10,
        EvaluationCategory.DIFFICULT: 7,
    }


def test_evaluation_cases_reference_known_documents():
    documents = load_evaluation_documents(
        DATA_DIRECTORY / "corpus.jsonl"
    )
    cases = load_evaluation_cases(
        DATA_DIRECTORY / "cases.jsonl"
    )

    document_keys = {
        document.key
        for document in documents
    }

    for case in cases:
        referenced_keys = (
            set(case.expected_document_keys)
            | set(case.forbidden_document_keys)
        )

        assert referenced_keys <= document_keys


def test_evaluation_document_keys_are_unique():
    documents = load_evaluation_documents(
        DATA_DIRECTORY / "corpus.jsonl"
    )

    document_keys = [
        document.key
        for document in documents
    ]

    assert len(document_keys) == len(
        set(document_keys)
    )


def test_evaluation_case_ids_are_unique():
    cases = load_evaluation_cases(
        DATA_DIRECTORY / "cases.jsonl"
    )

    case_ids = [
        case.id
        for case in cases
    ]

    assert len(case_ids) == len(
        set(case_ids)
    )


def test_evaluation_case_owners_exist_in_corpus():
    documents = load_evaluation_documents(
        DATA_DIRECTORY / "corpus.jsonl"
    )
    cases = load_evaluation_cases(
        DATA_DIRECTORY / "cases.jsonl"
    )

    owner_keys = {
        document.owner_key
        for document in documents
    }

    for case in cases:
        assert case.owner_key in owner_keys


def test_cross_user_cases_have_forbidden_documents():
    cases = load_evaluation_cases(
        DATA_DIRECTORY / "cases.jsonl"
    )

    cross_user_cases = [
        case
        for case in cases
        if (
            case.category
            == EvaluationCategory.CROSS_USER
        )
    ]

    assert len(cross_user_cases) == 10

    for case in cross_user_cases:
        assert case.expected_abstained is True
        assert case.expected_document_keys == ()
        assert case.forbidden_document_keys
