import json
from pathlib import Path

import pytest

from app.nlp.classifier import IntentClassifier
from training.train_model import load_training_examples, split_examples


BACKEND_DIR = Path(__file__).resolve().parents[1]
DATASET_PATH = BACKEND_DIR / "data" / "intents.json"


@pytest.fixture
def training_examples() -> tuple[list[str], list[str]]:
    return load_training_examples(DATASET_PATH)


def test_training_examples_exclude_fallback(
    training_examples: tuple[list[str], list[str]],
) -> None:
    patterns, labels = training_examples

    assert len(patterns) == 88
    assert len(patterns) == len(labels)
    assert "fallback" not in labels


def test_stratified_holdout_has_no_pattern_leakage(
    training_examples: tuple[list[str], list[str]],
) -> None:
    patterns, labels = training_examples

    x_train, x_test, y_train, y_test = split_examples(patterns, labels)

    assert not set(x_train).intersection(x_test)
    assert set(y_train) == set(labels)
    assert set(y_test) == set(labels)
    assert len(x_test) == 22


def test_fit_predict_and_probabilities(
    training_examples: tuple[list[str], list[str]],
) -> None:
    patterns, labels = training_examples
    classifier = IntentClassifier()
    classifier.fit(patterns, labels)

    prediction = classifier.predict("Where can I find the tuition fees?")

    assert prediction.predicted_intent == "fees_payment"
    assert prediction.is_fallback is False
    assert 0.0 <= prediction.confidence <= 1.0
    assert set(prediction.probabilities) == set(labels)
    assert sum(prediction.probabilities.values()) == pytest.approx(1.0)


def test_unknown_query_is_eligible_for_fallback(
    training_examples: tuple[list[str], list[str]],
) -> None:
    patterns, labels = training_examples
    classifier = IntentClassifier()
    classifier.fit(patterns, labels)

    prediction = classifier.predict("xylophonic quasar blorptastic")

    assert prediction.is_fallback is True
    assert prediction.predicted_intent in set(labels)


def test_unrelated_question_is_eligible_for_fallback(
    training_examples: tuple[list[str], list[str]],
) -> None:
    patterns, labels = training_examples
    classifier = IntentClassifier()
    classifier.fit(patterns, labels)

    prediction = classifier.predict("Can I get a bicycle repair near campus?")

    assert prediction.is_fallback is True


def test_confidence_threshold_is_configurable(
    training_examples: tuple[list[str], list[str]],
) -> None:
    patterns, labels = training_examples
    classifier = IntentClassifier(confidence_threshold=1.0)
    classifier.fit(patterns, labels)

    prediction = classifier.predict("Where can I find the tuition fees?")

    assert prediction.is_fallback is True


@pytest.mark.parametrize("threshold", [-0.01, 1.01, float("nan"), True])
def test_invalid_confidence_threshold_is_rejected(threshold: float) -> None:
    with pytest.raises(ValueError, match="confidence_threshold"):
        IntentClassifier(confidence_threshold=threshold)


def test_unfitted_classifier_rejects_prediction() -> None:
    with pytest.raises(RuntimeError, match="not been fitted or loaded"):
        IntentClassifier().predict("Where are the fees?")


def test_model_and_vectorizer_save_and_load(
    training_examples: tuple[list[str], list[str]],
    tmp_path: Path,
) -> None:
    patterns, labels = training_examples
    classifier = IntentClassifier()
    classifier.fit(patterns, labels)

    vectorizer_path, model_path = classifier.save(tmp_path / "artifacts")
    loaded = IntentClassifier.load(tmp_path / "artifacts")

    original_prediction = classifier.predict("Where can I find the tuition fees?")
    loaded_prediction = loaded.predict("Where can I find the tuition fees?")
    assert vectorizer_path.is_file()
    assert model_path.is_file()
    assert loaded_prediction == original_prediction


def test_training_loader_uses_existing_json_dataset() -> None:
    with DATASET_PATH.open(encoding="utf-8") as dataset_file:
        dataset = json.load(dataset_file)
    trainable_intents = [
        intent for intent in dataset["intents"] if intent["trainable"]
    ]

    patterns, labels = load_training_examples(DATASET_PATH)

    assert len(patterns) == sum(
        len(intent["patterns"]) for intent in trainable_intents
    )
    assert set(labels) == {intent["intent"] for intent in trainable_intents}
