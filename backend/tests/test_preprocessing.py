import pytest

from app.nlp.preprocessing import normalize_text


def test_normalize_text_lowercases_and_normalizes_whitespace() -> None:
    assert normalize_text("  HOW\tMuch   are Fees?  ") == "how much are fees"


def test_normalize_text_replaces_punctuation_without_merging_words() -> None:
    assert normalize_text("fees,course;library!") == "fees course library"


def test_normalize_text_applies_unicode_normalization() -> None:
    assert normalize_text("ＡＤＭＩＳＳＩＯＮ") == "admission"


def test_normalize_text_preserves_meaningful_words() -> None:
    assert normalize_text("Do I need to pay the fee?") == "do i need to pay the fee"


def test_normalize_text_rejects_non_string_input() -> None:
    with pytest.raises(TypeError, match="text must be a string"):
        normalize_text(None)  # type: ignore[arg-type]
