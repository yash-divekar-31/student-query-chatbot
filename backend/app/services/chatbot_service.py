"""Coordinate classifier inference and dataset-backed response mapping."""

import pickle
from dataclasses import dataclass
from pathlib import Path

from app.nlp.classifier import (
    DEFAULT_CONFIDENCE_THRESHOLD,
    IntentClassifier,
)
from app.services.response_service import ResponseService


class ChatbotInitializationError(RuntimeError):
    """Raised when the model or response dataset cannot be initialized."""


@dataclass(frozen=True)
class ChatbotAnswer:
    intent: str
    confidence: float
    response: str
    is_fallback: bool


class ChatbotService:
    """Use a loaded classifier and response map to answer student queries."""

    def __init__(
        self,
        classifier: IntentClassifier,
        response_service: ResponseService,
    ) -> None:
        self._classifier = classifier
        self._response_service = response_service

    @classmethod
    def from_files(
        cls,
        model_dir: Path,
        dataset_path: Path,
        confidence_threshold: float = DEFAULT_CONFIDENCE_THRESHOLD,
    ) -> "ChatbotService":
        """Load model artifacts and dataset once when the application starts."""
        try:
            classifier = IntentClassifier.load(
                model_dir,
                confidence_threshold=confidence_threshold,
            )
            response_service = ResponseService.from_file(dataset_path)
        except (
            AttributeError,
            EOFError,
            ImportError,
            OSError,
            pickle.UnpicklingError,
            TypeError,
            ValueError,
        ) as error:
            raise ChatbotInitializationError(
                "The chatbot model or response dataset could not be loaded."
            ) from error

        return cls(classifier, response_service)

    def answer(self, question: str) -> ChatbotAnswer:
        """Predict the query intent and map it to its configured response."""
        prediction = self._classifier.predict(question)
        mapped_response = self._response_service.resolve(prediction)
        return ChatbotAnswer(
            intent=mapped_response.intent,
            confidence=prediction.confidence,
            response=mapped_response.response,
            is_fallback=mapped_response.is_fallback,
        )
