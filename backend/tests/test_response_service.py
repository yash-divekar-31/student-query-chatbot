from app.nlp.classifier import Prediction
from app.services.response_service import ResponseService


def make_service() -> ResponseService:
    return ResponseService(
        {
            "fees_payment": ["SAMPLE PLACEHOLDER: Check official fee information."],
            "fallback": ["Please rephrase your question or consult official sources."],
        }
    )


def test_response_is_mapped_from_the_predicted_intent() -> None:
    service = make_service()
    prediction = Prediction(
        predicted_intent="fees_payment",
        confidence=0.8,
        probabilities={"fees_payment": 0.8},
        is_fallback=False,
    )

    result = service.resolve(prediction)

    assert result.intent == "fees_payment"
    assert result.response.startswith("SAMPLE PLACEHOLDER:")
    assert result.is_fallback is False


def test_low_confidence_prediction_uses_fallback_response() -> None:
    service = make_service()
    prediction = Prediction(
        predicted_intent="fees_payment",
        confidence=0.2,
        probabilities={"fees_payment": 0.2},
        is_fallback=True,
    )

    result = service.resolve(prediction)

    assert result.intent == "fallback"
    assert result.response == "Please rephrase your question or consult official sources."
    assert result.is_fallback is True


def test_invalid_or_unmapped_prediction_uses_fallback() -> None:
    service = make_service()
    prediction = Prediction(
        predicted_intent="unknown_intent",
        confidence=0.9,
        probabilities={"unknown_intent": 0.9},
        is_fallback=False,
    )

    result = service.resolve(prediction)

    assert result.intent == "fallback"
    assert result.is_fallback is True


def test_prediction_without_a_mapped_response_uses_fallback() -> None:
    service = ResponseService(
        {"fallback": ["Please rephrase your question or consult official sources."]}
    )
    prediction = Prediction(
        predicted_intent="fees_payment",
        confidence=0.9,
        probabilities={"fees_payment": 0.9},
        is_fallback=False,
    )

    result = service.resolve(prediction)

    assert result.intent == "fallback"
    assert result.is_fallback is True


def test_dataset_fallback_prediction_uses_fallback_response() -> None:
    service = make_service()
    prediction = Prediction(
        predicted_intent="fallback",
        confidence=0.9,
        probabilities={"fallback": 0.9},
        is_fallback=False,
    )

    result = service.resolve(prediction)

    assert result.intent == "fallback"
    assert result.is_fallback is True
