"""Evaluate, train, and save the student-query intent classifier."""

import argparse
import csv
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Sequence

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.dummy import DummyClassifier
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
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
EVALUATION_DIR = BACKEND_DIR.parent / "docs" / "evaluation"


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


def save_evaluation(
    evaluation_dir: Path,
    *,
    dataset_path: Path,
    x_train: Sequence[str],
    x_test: Sequence[str],
    y_train: Sequence[str],
    y_test: Sequence[str],
    predictions: Sequence[str],
    metrics: dict[str, float],
    random_state: int,
    test_size: float,
    confidence_threshold: float,
) -> None:
    """Write machine-readable metrics, per-class metrics, and a confusion matrix."""
    evaluation_dir.mkdir(parents=True, exist_ok=True)
    intent_names = sorted(set(y_test))
    try:
        dataset_label = str(dataset_path.resolve().relative_to(BACKEND_DIR.parent))
    except ValueError:
        dataset_label = str(dataset_path)

    report = classification_report(
        y_test,
        predictions,
        labels=intent_names,
        output_dict=True,
        zero_division=0,
    )
    baseline = DummyClassifier(strategy="most_frequent")
    baseline.fit(list(x_train), list(y_train))
    baseline_predictions = baseline.predict(list(x_test))
    baseline_metrics = {
        "accuracy": float(accuracy_score(y_test, baseline_predictions)),
        "macro_precision": float(
            precision_score(y_test, baseline_predictions, average="macro", zero_division=0)
        ),
        "macro_recall": float(
            recall_score(y_test, baseline_predictions, average="macro", zero_division=0)
        ),
        "macro_f1": float(
            f1_score(y_test, baseline_predictions, average="macro", zero_division=0)
        ),
    }

    results = {
        "dataset": dataset_label,
        "methodology": {
            "split": "stratified train_test_split",
            "test_size": test_size,
            "random_state": random_state,
            "training_examples": len(x_train),
            "holdout_examples": len(x_test),
            "holdout_intents": len(intent_names),
            "confidence_threshold": confidence_threshold,
            "note": "Top-label metrics do not apply fallback threshold mapping.",
        },
        "model": {
            "accuracy": metrics["accuracy"],
            "macro_precision": metrics["macro_precision"],
            "macro_recall": metrics["macro_recall"],
            "macro_f1": metrics["macro_f1"],
            "per_class": {
                intent: {
                    "precision": float(report[intent]["precision"]),
                    "recall": float(report[intent]["recall"]),
                    "f1_score": float(report[intent]["f1-score"]),
                    "support": int(report[intent]["support"]),
                }
                for intent in intent_names
            },
        },
        "baseline": {
            "type": "DummyClassifier(most_frequent)",
            **baseline_metrics,
        },
    }
    evaluation_json = evaluation_dir / "model_evaluation.json"
    with evaluation_json.open("w", encoding="utf-8") as output_file:
        json.dump(results, output_file, indent=2)
        output_file.write("\n")

    csv_path = evaluation_dir / "per_class_metrics.csv"
    with csv_path.open("w", encoding="utf-8", newline="") as output_file:
        writer = csv.writer(output_file)
        writer.writerow(["intent", "precision", "recall", "f1_score", "support"])
        for intent in intent_names:
            class_metrics = results["model"]["per_class"][intent]
            writer.writerow([
                intent,
                f'{class_metrics["precision"]:.6f}',
                f'{class_metrics["recall"]:.6f}',
                f'{class_metrics["f1_score"]:.6f}',
                class_metrics["support"],
            ])

    matrix = confusion_matrix(y_test, predictions, labels=intent_names)
    figure_width = max(10, len(intent_names) * 0.55)
    figure, axis = plt.subplots(figsize=(figure_width, figure_width))
    image = axis.imshow(matrix, interpolation="nearest", cmap="Blues")
    figure.colorbar(image, ax=axis)
    axis.set(
        xticks=range(len(intent_names)),
        yticks=range(len(intent_names)),
        xticklabels=intent_names,
        yticklabels=intent_names,
        ylabel="Actual intent",
        xlabel="Predicted intent",
    )
    plt.setp(axis.get_xticklabels(), rotation=90, ha="right", fontsize=7)
    plt.setp(axis.get_yticklabels(), fontsize=7)
    axis.set_title("Holdout Confusion Matrix")
    figure.tight_layout()
    figure.savefig(evaluation_dir / "confusion_matrix.png", dpi=180)
    plt.close(figure)


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
    parser.add_argument(
        "--evaluation-dir",
        type=Path,
        default=EVALUATION_DIR,
        help="Directory for evaluation JSON, CSV, and confusion matrix files.",
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

        save_evaluation(
            args.evaluation_dir,
            dataset_path=args.dataset,
            x_train=x_train,
            x_test=x_test,
            y_train=y_train,
            y_test=y_test,
            predictions=predictions,
            metrics=metrics,
            random_state=RANDOM_STATE,
            test_size=TEST_SIZE,
            confidence_threshold=args.confidence_threshold,
        )
        print(f"Saved evaluation JSON: {args.evaluation_dir / 'model_evaluation.json'}")
        print(f"Saved per-class CSV: {args.evaluation_dir / 'per_class_metrics.csv'}")
        print(
            "Saved confusion matrix: "
            f"{args.evaluation_dir / 'confusion_matrix.png'}"
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
