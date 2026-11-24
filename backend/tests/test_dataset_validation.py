import copy
import json
from pathlib import Path
from typing import Any

import pytest

from training.validate_dataset import validate_dataset


DATASET_PATH = Path(__file__).resolve().parents[1] / "data" / "intents.json"


@pytest.fixture
def valid_dataset() -> dict[str, Any]:
    with DATASET_PATH.open(encoding="utf-8") as dataset_file:
        return json.load(dataset_file)


def test_sample_dataset_is_valid(valid_dataset: dict[str, Any]) -> None:
    assert validate_dataset(valid_dataset) == []


def test_validation_reports_missing_required_intent(
    valid_dataset: dict[str, Any],
) -> None:
    dataset = copy.deepcopy(valid_dataset)
    dataset["intents"] = [
        item for item in dataset["intents"] if item["intent"] != "library"
    ]

    errors = validate_dataset(dataset)

    assert "Required intent 'library' is missing." in errors


def test_validation_reports_duplicate_pattern_after_normalization(
    valid_dataset: dict[str, Any],
) -> None:
    dataset = copy.deepcopy(valid_dataset)
    dataset["intents"][1]["patterns"][0] = " HELLO!!! "

    errors = validate_dataset(dataset)

    assert any("Duplicate pattern" in error for error in errors)


def test_validation_reports_insufficient_training_examples(
    valid_dataset: dict[str, Any],
) -> None:
    dataset = copy.deepcopy(valid_dataset)
    dataset["intents"][1]["patterns"] = ["How do I apply?"]

    errors = validate_dataset(dataset, min_patterns=3)

    assert any("at least 3 are required" in error for error in errors)


@pytest.mark.parametrize(
    ("field", "value", "expected_error"),
    [
        ("category", "", ".category must be a non-empty string"),
        ("trainable", "yes", ".trainable must be a boolean"),
        ("patterns", "not a list", ".patterns must be a list"),
        ("responses", [], ".responses must be a non-empty list"),
        ("response_status", [], ".response_status must be one of"),
    ],
)
def test_validation_reports_invalid_fields(
    valid_dataset: dict[str, Any],
    field: str,
    value: Any,
    expected_error: str,
) -> None:
    dataset = copy.deepcopy(valid_dataset)
    dataset["intents"][0][field] = value

    errors = validate_dataset(dataset)

    assert any(expected_error in error for error in errors)


def test_validation_reports_duplicate_intent_names(
    valid_dataset: dict[str, Any],
) -> None:
    dataset = copy.deepcopy(valid_dataset)
    duplicate = copy.deepcopy(dataset["intents"][0])
    dataset["intents"].append(duplicate)

    errors = validate_dataset(dataset)

    assert "Duplicate intent name: 'greeting'." in errors


def test_validation_rejects_non_object_dataset() -> None:
    assert validate_dataset([]) == ["Dataset root must be a JSON object."]


def test_validation_reports_missing_dataset_metadata(
    valid_dataset: dict[str, Any],
) -> None:
    dataset = copy.deepcopy(valid_dataset)
    del dataset["dataset_name"]

    errors = validate_dataset(dataset)

    assert "The 'dataset_name' field must be a non-empty string." in errors
