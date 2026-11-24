"""Text normalization shared by TF-IDF training and inference."""

import re
import unicodedata


_PUNCTUATION_OR_UNDERSCORE = re.compile(r"[^\w\s]|_", flags=re.UNICODE)
_WHITESPACE = re.compile(r"\s+")


def normalize_text(text: str) -> str:
    """Normalize casing, Unicode, punctuation, and whitespace without removing words."""
    if not isinstance(text, str):
        raise TypeError("text must be a string")

    normalized = unicodedata.normalize("NFKC", text).lower()
    normalized = _PUNCTUATION_OR_UNDERSCORE.sub(" ", normalized)
    return _WHITESPACE.sub(" ", normalized).strip()
