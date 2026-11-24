import json
from pathlib import Path
from typing import Iterator

import pytest
from fastapi.testclient import TestClient

from app.main import app, create_app


BACKEND_DIR = Path(__file__).resolve().parents[1]
DATASET_PATH = BACKEND_DIR / "data" / "intents.json"


@pytest.fixture(scope="module")
def client() -> Iterator[TestClient]:
    with TestClient(app) as test_client:
        yield test_client


def test_chat_returns_dataset_response_for_known_question(
    client: TestClient,
) -> None:
    response = client.post(
        "/chat",
        json={"question": "How do students pay their fees?"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["question"] == "How do students pay their fees?"
    assert body["intent"] == "fees_payment"
    assert body["confidence"] > 0.0
    assert body["response"].startswith("SAMPLE PLACEHOLDER:")
    assert body["is_fallback"] is False


def test_low_confidence_holdout_question_returns_fallback(
    client: TestClient,
) -> None:
    response = client.post(
        "/chat",
        json={"question": "Where can I find the tuition fees?"},
    )

    assert response.status_code == 200
    assert response.json()["intent"] == "fallback"
    assert response.json()["is_fallback"] is True


def test_unknown_question_returns_dataset_fallback(
    client: TestClient,
) -> None:
    response = client.post(
        "/chat",
        json={"question": "xylophonic quasar blorptastic"},
    )

    with DATASET_PATH.open(encoding="utf-8") as dataset_file:
        dataset = json.load(dataset_file)
    fallback = next(
        item for item in dataset["intents"] if item["intent"] == "fallback"
    )

    assert response.status_code == 200
    assert response.json()["intent"] == "fallback"
    assert response.json()["response"] == fallback["responses"][0]
    assert response.json()["is_fallback"] is True


@pytest.mark.parametrize(
    "payload",
    [
        {"question": ""},
        {"question": "   "},
        {"question": "?!"},
        {"question": "x" * 501},
        {"question": 42},
        {},
        {"question": "fees", "unexpected": True},
    ],
)
def test_chat_rejects_invalid_input(
    client: TestClient,
    payload: dict[str, object],
) -> None:
    response = client.post("/chat", json=payload)

    assert response.status_code == 422


def test_chat_accepts_question_at_maximum_length(client: TestClient) -> None:
    response = client.post("/chat", json={"question": "fees " * 100})

    assert response.status_code == 200


@pytest.mark.parametrize(
    ("question", "expected_intent"),
    [
        ("hOw dO sTuDeNtS pAy tHeIr fEeS?", "fees_payment"),
        ("whre cn i fynd fees", "fees_payment"),
        ("What is the fee for 123?", "fees_payment"),
    ],
)
def test_chat_handles_normalized_and_noisy_questions(
    client: TestClient,
    question: str,
    expected_intent: str,
) -> None:
    response = client.post("/chat", json={"question": question})

    assert response.status_code == 200
    assert response.json()["intent"] == expected_intent
    assert response.json()["is_fallback"] is False


def test_repeated_questions_return_consistent_responses(
    client: TestClient,
) -> None:
    payload = {"question": "Where can I find the tuition fees?"}

    first = client.post("/chat", json=payload).json()
    second = client.post("/chat", json=payload).json()

    assert first == second


def test_low_confidence_prediction_returns_fallback() -> None:
    strict_app = create_app(confidence_threshold=1.0)

    with TestClient(strict_app) as strict_client:
        response = strict_client.post(
            "/chat",
            json={"question": "Where can I find the tuition fees?"},
        )

    assert response.status_code == 200
    assert response.json()["intent"] == "fallback"
    assert response.json()["is_fallback"] is True


def test_missing_model_artifacts_return_safe_service_error(
    tmp_path: Path,
) -> None:
    unavailable_app = create_app(model_dir=tmp_path / "missing-model")

    with TestClient(unavailable_app) as unavailable_client:
        response = unavailable_client.post(
            "/chat",
            json={"question": "Where can I find the tuition fees?"},
        )

    assert response.status_code == 503
    assert response.json() == {
        "detail": "The chatbot is temporarily unavailable. Please try again later."
    }
    assert str(tmp_path) not in response.text
