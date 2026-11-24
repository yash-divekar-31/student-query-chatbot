"""Validate the student-query intent dataset."""

import json
import re
import sys
from pathlib import Path
from typing import Any


DATASET_PATH = Path(__file__).resolve().parents[1] / "data" / "intents.json"
MIN_PATTERNS_PER_INTENT = 3
VALID_RESPONSE_STATUSES = {"placeholder", "generic"}
REQUIRED_INTENTS = {
    "greeting",
    "admission_process",
    "admission_eligibility",
    "application_documents",
    "application_status",
    "courses_departments",
    "fees_payment",
    "scholarships",
    "examinations",
    "results",
    "attendance",
    "placements",
    "internships",
    "training_development",
    "campus_facilities",
    "library",
    "hostel",
    "transportation",
    "contact_information",
    "academic_calendar",
    "general_faq",
    "goodbye",
    "fallback",
}


def _normalize_pattern(pattern: str) -> str:
    """Normalize case, punctuation, and repeated whitespace for duplicate checks."""
    return re.sub(r"[^\w]+", " ", pattern.casefold()).strip()


def validate_dataset(
    dataset: Any,
    min_patterns: int = MIN_PATTERNS_PER_INTENT,
) -> list[str]:
    """Return all schema and content validation errors found in a dataset."""
    errors: list[str] = []
    if not isinstance(min_patterns, int) or min_patterns < 1:
        return ["min_patterns must be a positive integer."]

    if not isinstance(dataset, dict):
        return ["Dataset root must be a JSON object."]

    for field in ("schema_version", "dataset_name", "college_data_status"):
        value = dataset.get(field)
        if not isinstance(value, str) or not value.strip():
            errors.append(f"The '{field}' field must be a non-empty string.")

    intents = dataset.get("intents")
    if not isinstance(intents, list):
        errors.append("The 'intents' field must be a list.")
        return errors

    seen_intents: set[str] = set()
    seen_patterns: dict[str, str] = {}

    for index, item in enumerate(intents):
        location = f"intents[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{location} must be an object.")
            continue

        intent_name = item.get("intent")
        if not isinstance(intent_name, str) or not intent_name.strip():
            errors.append(f"{location}.intent must be a non-empty string.")
            intent_name = ""
        else:
            intent_name = intent_name.strip()
            if intent_name in seen_intents:
                errors.append(f"Duplicate intent name: '{intent_name}'.")
            seen_intents.add(intent_name)

        category = item.get("category")
        if not isinstance(category, str) or not category.strip():
            errors.append(f"{location}.category must be a non-empty string.")

        trainable = item.get("trainable")
        if not isinstance(trainable, bool):
            errors.append(f"{location}.trainable must be a boolean.")

        response_status = item.get("response_status")
        if (
            not isinstance(response_status, str)
            or response_status not in VALID_RESPONSE_STATUSES
        ):
            errors.append(
                f"{location}.response_status must be one of "
                f"{sorted(VALID_RESPONSE_STATUSES)}."
            )

        patterns = item.get("patterns")
        if not isinstance(patterns, list):
            errors.append(f"{location}.patterns must be a list.")
        else:
            if len(patterns) < min_patterns:
                errors.append(
                    f"{location}.patterns has {len(patterns)} examples; "
                    f"at least {min_patterns} are required."
                )
            for pattern_index, pattern in enumerate(patterns):
                pattern_location = f"{location}.patterns[{pattern_index}]"
                if not isinstance(pattern, str) or not pattern.strip():
                    errors.append(f"{pattern_location} must be a non-empty string.")
                    continue

                normalized = _normalize_pattern(pattern)
                if not normalized:
                    errors.append(
                        f"{pattern_location} must contain letters or numbers."
                    )
                    continue

                previous_intent = seen_patterns.get(normalized)
                if previous_intent is not None:
                    errors.append(
                        f"Duplicate pattern '{pattern.strip()}' in intent "
                        f"'{intent_name}'; it already appears in "
                        f"'{previous_intent}'."
                    )
                else:
                    seen_patterns[normalized] = intent_name

        responses = item.get("responses")
        if not isinstance(responses, list) or not responses:
            errors.append(f"{location}.responses must be a non-empty list.")
        else:
            for response_index, response in enumerate(responses):
                if not isinstance(response, str) or not response.strip():
                    errors.append(
                        f"{location}.responses[{response_index}] "
                        "must be a non-empty string."
                    )

    missing_intents = REQUIRED_INTENTS - seen_intents
    for missing_intent in sorted(missing_intents):
        errors.append(f"Required intent '{missing_intent}' is missing.")

    fallback = next(
        (
            item
            for item in intents
            if isinstance(item, dict) and item.get("intent") == "fallback"
        ),
        None,
    )
    if fallback is not None and fallback.get("trainable") is not False:
        errors.append("The 'fallback' intent must have trainable set to false.")

    return errors


def main() -> int:
    """Validate the checked-in sample dataset and print a concise result."""
    try:
        with DATASET_PATH.open(encoding="utf-8") as dataset_file:
            dataset = json.load(dataset_file)
    except (OSError, json.JSONDecodeError) as error:
        print(f"Could not read dataset at {DATASET_PATH}: {error}", file=sys.stderr)
        return 1

    errors = validate_dataset(dataset)
    if errors:
        print("Dataset validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    trainable_count = sum(
        item["trainable"] for item in dataset["intents"]
    )
    pattern_count = sum(len(item["patterns"]) for item in dataset["intents"])
    print(
        f"Dataset is valid: {len(dataset['intents'])} intents, "
        f"{trainable_count} trainable intents, {pattern_count} patterns."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
