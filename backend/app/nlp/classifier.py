"""TF-IDF and Logistic Regression classifier for student-query intents."""

from dataclasses import dataclass
from math import isfinite
from pathlib import Path
from typing import Sequence

import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

from app.nlp.preprocessing import normalize_text


DEFAULT_CONFIDENCE_THRESHOLD = 0.065
VECTOR_FILE_NAME = "tfidf_vectorizer.joblib"
CLASSIFIER_FILE_NAME = "logistic_regression.joblib"


@dataclass(frozen=True)
class Prediction:
    predicted_intent: str
    confidence: float
    probabilities: dict[str, float]
    is_fallback: bool


class IntentClassifier:
    """Fit, persist, load, and query an intent classifier."""

    def __init__(
        self,
        confidence_threshold: float = DEFAULT_CONFIDENCE_THRESHOLD,
    ) -> None:
        if (
            isinstance(confidence_threshold, bool)
            or not isinstance(confidence_threshold, (int, float))
            or not isfinite(confidence_threshold)
            or not 0.0 <= confidence_threshold <= 1.0
        ):
            raise ValueError("confidence_threshold must be a number from 0 to 1.")

        self.confidence_threshold = float(confidence_threshold)
        self.vectorizer: TfidfVectorizer | None = None
        self.model: LogisticRegression | None = None

    def fit(self, patterns: Sequence[str], labels: Sequence[str]) -> None:
        """Fit TF-IDF and Logistic Regression from paired example questions."""
        if len(patterns) != len(labels):
            raise ValueError("patterns and labels must have the same number of items.")
        if not patterns:
            raise ValueError("At least one training example is required.")
        if len(set(labels)) < 2:
            raise ValueError("Training requires at least two distinct intent labels.")
        if any(not isinstance(text, str) or not normalize_text(text) for text in patterns):
            raise ValueError("Every training pattern must contain searchable text.")
        if any(not isinstance(label, str) or not label.strip() for label in labels):
            raise ValueError("Every training label must be a non-empty string.")

        vectorizer = TfidfVectorizer(
            analyzer="char_wb",
            lowercase=False,
            ngram_range=(2, 5),
            preprocessor=normalize_text,
            sublinear_tf=True,
        )
        features = vectorizer.fit_transform(patterns)
        model = LogisticRegression(max_iter=1000, random_state=42)
        model.fit(features, labels)

        self.vectorizer = vectorizer
        self.model = model

    def predict(self, text: str) -> Prediction:
        """Return the top intent, its probability, all class probabilities, and fallback status."""
        if not isinstance(text, str) or not normalize_text(text):
            raise ValueError("A non-empty text query is required.")
        if self.vectorizer is None or self.model is None:
            raise RuntimeError("The classifier has not been fitted or loaded.")

        features = self.vectorizer.transform([text])
        class_probabilities = self.model.predict_proba(features)[0]
        probabilities = {
            str(intent): float(probability)
            for intent, probability in zip(
                self.model.classes_,
                class_probabilities,
            )
        }
        ranked_probabilities = dict(
            sorted(
                probabilities.items(),
                key=lambda item: item[1],
                reverse=True,
            )
        )
        predicted_intent = next(iter(ranked_probabilities))
        confidence = ranked_probabilities[predicted_intent]

        return Prediction(
            predicted_intent=predicted_intent,
            confidence=confidence,
            probabilities=ranked_probabilities,
            is_fallback=features.nnz == 0 or confidence < self.confidence_threshold,
        )

    def save(self, model_dir: Path) -> tuple[Path, Path]:
        """Save the fitted vectorizer and classifier as separate Joblib artifacts."""
        if self.vectorizer is None or self.model is None:
            raise RuntimeError("Fit the classifier before saving it.")

        model_dir.mkdir(parents=True, exist_ok=True)
        vectorizer_path = model_dir / VECTOR_FILE_NAME
        classifier_path = model_dir / CLASSIFIER_FILE_NAME
        joblib.dump(self.vectorizer, vectorizer_path)
        joblib.dump(self.model, classifier_path)
        return vectorizer_path, classifier_path

    @classmethod
    def load(
        cls,
        model_dir: Path,
        confidence_threshold: float = DEFAULT_CONFIDENCE_THRESHOLD,
    ) -> "IntentClassifier":
        """Load Joblib artifacts created by this project."""
        vectorizer_path = model_dir / VECTOR_FILE_NAME
        classifier_path = model_dir / CLASSIFIER_FILE_NAME
        if not vectorizer_path.is_file() or not classifier_path.is_file():
            raise FileNotFoundError(
                f"Expected both {VECTOR_FILE_NAME} and {CLASSIFIER_FILE_NAME} "
                f"inside {model_dir}."
            )

        instance = cls(confidence_threshold=confidence_threshold)
        vectorizer = joblib.load(vectorizer_path)
        model = joblib.load(classifier_path)
        if not isinstance(vectorizer, TfidfVectorizer):
            raise TypeError(f"{vectorizer_path} is not a TF-IDF vectorizer.")
        if not isinstance(model, LogisticRegression):
            raise TypeError(f"{classifier_path} is not a Logistic Regression model.")

        instance.vectorizer = vectorizer
        instance.model = model
        return instance
