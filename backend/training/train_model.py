"""Evaluate, train, and save the student-query intent classifier."""

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Sequence

from sklearn.metrics import (
    accuracy_score,
    classification_report,
    f1_score,
    precision_score,
    recall_score,
)
from sklearn.model_selection import train_test_split

from app.nlp.classifier import (
    DEFAULT_CONFIDENCE_THRESHOLD,
    IntentClassifier,
)
from training.validate_dataset import validate_dataset


BACKEND_DIR = Path(__file__).resolve().parents[1]
DATASET_PATH = BACKEND_DIR / "data" / "intents.json"
MODEL_DIR = BACKEND_DIR / "models"
TEST_SIZE = 0.25
RANDOM_STATE = 42


def load_training_examples(dataset_path: Path) -> tuple[list[str], list[str]]:
    """Load and validate patterns from trainable intents only."""
    try:
        with dataset_path.open(encoding="utf-8") as dataset_file:
            dataset = json.load(dataset_file)
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError(f"Could not read dataset at {dataset_path}: {error}") from error

    errors = validate_dataset(dataset)
    if errors:
        raise ValueError("Invalid intent dataset:\n- " + "\n- ".join(errors))

    patterns: list[str] = []
    labels: list[str] = []
    for intent in dataset["intents"]:
        if not intent["trainable"]:
            continue
        patterns.extend(intent["patterns"])
        labels.extend([intent["intent"]] * len(intent["patterns"]))

    if not patterns:
        raise ValueError("The dataset has no trainable intent patterns.")

    return patterns, labels


def split_examples(
    patterns: Sequence[str],
    labels: Sequence[str],
    test_size: float = TEST_SIZE,
    random_state: int = RANDOM_STATE,
) -> tuple[list[str], list[str], list[str], list[str]]:
    """Create a stratified holdout split with examples from every intent in both sets."""
    if len(patterns) != len(labels):
        raise ValueError("patterns and labels must have the same number of items.")
    if not 0.0 < test_size < 1.0:
        raise ValueError("test_size must be greater than 0 and less than 1.")

    label_counts = Counter(labels)
    insufficient = sorted(label for label, count in label_counts.items() if count < 2)
    if insufficient:
        raise ValueError(
            "Stratified evaluation needs at least two examples per intent; "
            f"insufficient examples for: {', '.join(insufficient)}."
        )

    try:
        return train_test_split(
            list(patterns),
            list(labels),
            test_size=test_size,
            random_state=random_state,
            stratify=list(labels),
        )
    except ValueError as error:
        raise ValueError(f"Could not create a stratified holdout split: {error}") from error


def evaluate_holdout(
    classifier: IntentClassifier,
    patterns: Sequence[str],
    labels: Sequence[str],
) -> tuple[dict[str, float], list[str]]:
    """Calculate classification metrics from untouched holdout examples."""
    predictions = [
        classifier.predict(pattern).predicted_intent for pattern in patterns
    ]
    metrics = {
        "accuracy": float(accuracy_score(labels, predictions)),
        "macro_precision": float(
            precision_score(labels, predictions, average="macro", zero_division=0)
        ),
        "macro_recall": float(
            recall_score(labels, predictions, average="macro", zero_division=0)
        ),
        "macro_f1": float(
            f1_score(labels, predictions, average="macro", zero_division=0)
        ),
    }
    return metrics, predictions


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Evaluate and train the student-query intent classifier."
    )
    parser.add_argument(
        "--dataset",
        type=Path,
        default=DATASET_PATH,
        help="Path to the intent JSON dataset.",
    )
    parser.add_argument(
        "--model-dir",
        type=Path,
        default=MODEL_DIR,
        help="Directory for the saved TF-IDF and classifier artifacts.",
    )
    parser.add_argument(
        "--confidence-threshold",
        type=float,
        default=DEFAULT_CONFIDENCE_THRESHOLD,
        help="Mark predictions below this probability as fallback-eligible (0 to 1).",
    )
    args = parser.parse_args()

    try:
        patterns, labels = load_training_examples(args.dataset)
        x_train, x_test, y_train, y_test = split_examples(patterns, labels)

        classifier = IntentClassifier(
            confidence_threshold=args.confidence_threshold,
        )
        classifier.fit(x_train, y_train)
        metrics, predictions = evaluate_holdout(classifier, x_test, y_test)

        print(
            f"Holdout evaluation: {len(x_test)} examples "
            f"({TEST_SIZE:.0%} stratified; {len(set(y_test))} intents)"
        )
        for metric, score in metrics.items():
            print(f"{metric}: {score:.4f}")
        print("Per-intent holdout report:")
        intent_names = sorted(set(labels))
        print(
            classification_report(
                y_test,
                predictions,
                labels=intent_names,
                target_names=intent_names,
                zero_division=0,
            )
        )
        print(
            "Note: each intent has one holdout example; these metrics are "
            "illustrative for this small sample and are not a reliable "
            "estimate of real-world performance."
        )

        vectorizer_path, classifier_path = classifier.save(args.model_dir)
        print(
            f"Saved model trained on {len(x_train)} examples; "
            f"the {len(x_test)} holdout examples were excluded from training."
        )
        print(f"Saved TF-IDF vectorizer: {vectorizer_path}")
        print(f"Saved Logistic Regression model: {classifier_path}")
        return 0
    except (OSError, ValueError) as error:
        print(f"Training failed: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
