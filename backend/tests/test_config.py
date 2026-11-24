import pytest
from pydantic import ValidationError

from app.core.config import Settings


def test_settings_accept_single_cors_origin(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CORS_ORIGINS", "https://example.vercel.app")

    settings = Settings(_env_file=None)

    assert settings.cors_origins == ["https://example.vercel.app"]


def test_settings_split_comma_separated_cors_origins(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv(
        "CORS_ORIGINS",
        "https://example.vercel.app,http://localhost:5173",
    )

    settings = Settings(_env_file=None)

    assert settings.cors_origins == [
        "https://example.vercel.app",
        "http://localhost:5173",
    ]


def test_settings_default_cors_origins_are_preserved(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("CORS_ORIGINS", raising=False)

    settings = Settings(_env_file=None)

    assert settings.cors_origins == [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]


@pytest.mark.parametrize("value", ["*", "https://example.vercel.app, *"])
def test_settings_reject_wildcard_cors_origin(
    monkeypatch: pytest.MonkeyPatch,
    value: str,
) -> None:
    monkeypatch.setenv("CORS_ORIGINS", value)

    with pytest.raises(ValidationError, match="Wildcard CORS origins are not allowed"):
        Settings(_env_file=None)


@pytest.mark.parametrize("value", ["", " , , "])
def test_settings_handle_empty_cors_origins(
    monkeypatch: pytest.MonkeyPatch,
    value: str,
) -> None:
    monkeypatch.setenv("CORS_ORIGINS", value)

    settings = Settings(_env_file=None)

    assert settings.cors_origins == []
