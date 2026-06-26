import pytest

from app.chunker import split_text


def test_split_text_returns_empty_list_for_empty_text():
    result = split_text("")

    assert result == []


def test_split_text_returns_empty_list_for_blank_text():
    result = split_text("   ")

    assert result == []


def test_split_text_returns_single_chunk_when_text_is_smaller_than_chunk_size():
    result = split_text("short text", chunk_size=50, overlap=5)

    assert result == ["short text"]


def test_split_text_removes_leading_and_trailing_spaces():
    result = split_text("   clean text   ", chunk_size=50, overlap=5)

    assert result == ["clean text"]


def test_split_text_splits_text_into_multiple_chunks():
    result = split_text("abcdefghijklmnopqrstuvwxyz", chunk_size=10, overlap=0)

    assert result == [
        "abcdefghij",
        "klmnopqrst",
        "uvwxyz",
    ]


def test_split_text_applies_overlap_between_chunks():
    result = split_text("abcdefghijklmnopqrstuvwxyz", chunk_size=10, overlap=2)

    assert result == [
        "abcdefghij",
        "ijklmnopqr",
        "qrstuvwxyz",
    ]


def test_split_text_rejects_chunk_size_equal_to_zero():
    with pytest.raises(ValueError, match="chunk_size must be greater than zero"):
        split_text("some text", chunk_size=0, overlap=0)


def test_split_text_rejects_negative_chunk_size():
    with pytest.raises(ValueError, match="chunk_size must be greater than zero"):
        split_text("some text", chunk_size=-1, overlap=0)


def test_split_text_rejects_negative_overlap():
    with pytest.raises(ValueError, match="overlap must be greater than or equal to zero"):
        split_text("some text", chunk_size=10, overlap=-1)


def test_split_text_rejects_overlap_equal_to_chunk_size():
    with pytest.raises(ValueError, match="overlap must be smaller than chunk_size"):
        split_text("some text", chunk_size=10, overlap=10)


def test_split_text_rejects_overlap_greater_than_chunk_size():
    with pytest.raises(ValueError, match="overlap must be smaller than chunk_size"):
        split_text("some text", chunk_size=10, overlap=11)
