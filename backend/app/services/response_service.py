"""Map classifier predictions to responses stored in the intent dataset."""

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping, Sequence

from app.nlp.classifier import Prediction
from training.validate_dataset import validate_dataset


FALLBACK_INTENT = "fallback"


@dataclass(frozen=True)
class MappedResponse:
    intent: str
    response: str
    is_fallback: bool


class ResponseService:
    """Resolve intent predictions using only responses from the dataset."""

    def __init__(self, responses_by_intent: Mapping[str, Sequence[str]]) -> None:
        self._responses_by_intent: dict[str, tuple[str, ...]] = {}
        for intent, responses in responses_by_intent.items():
            if (
                not isinstance(intent, str)
                or not intent.strip()
                or not isinstance(responses, (list, tuple))
                or not responses
                or any(not isinstance(response, str) or not response.strip() for response in responses)
            ):
                raise ValueError("Intent responses must map labels to non-empty strings.")
            self._responses_by_intent[intent] = tuple(responses)

        if FALLBACK_INTENT not in self._responses_by_intent:
            raise ValueError("The dataset must provide a fallback response.")

    @classmethod
    def from_file(cls, dataset_path: Path) -> "ResponseService":
        """Load and validate responses from the configured intent JSON file."""
        try:
            with dataset_path.open(encoding="utf-8") as dataset_file:
                dataset = json.load(dataset_file)
        except (OSError, json.JSONDecodeError) as error:
            raise ValueError(f"Could not read response dataset: {error}") from error

        errors = validate_dataset(dataset)
        if errors:
            raise ValueError("Invalid response dataset:\n- " + "\n- ".join(errors))

        response_map = {
            item["intent"]: item["responses"]
            for item in dataset["intents"]
        }
        return cls(response_map)

    def resolve(self, prediction: Prediction) -> MappedResponse:
        """Return the matching response or the dataset fallback."""
        if prediction.is_fallback:
            return self._fallback_response()

        responses = self._responses_by_intent.get(prediction.predicted_intent)
        if not responses or prediction.predicted_intent == FALLBACK_INTENT:
            return self._fallback_response()

        return MappedResponse(
            intent=prediction.predicted_intent,
            response=responses[0],
            is_fallback=False,
        )

    def _fallback_response(self) -> MappedResponse:
        return MappedResponse(
            intent=FALLBACK_INTENT,
            response=self._responses_by_intent[FALLBACK_INTENT][0],
            is_fallback=True,
        )
