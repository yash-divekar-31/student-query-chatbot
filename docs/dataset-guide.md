# Dataset Guide

## Dataset status and location

The current dataset is [backend/data/intents.json](../backend/data/intents.json).
It is a temporary sample dataset with `college_data_status` set to
`sample_only_no_official_college_data`. It contains no verified college
specific facts.

Responses about institutional topics retain the prefix
`SAMPLE PLACEHOLDER:`. Greetings, goodbye, and fallback messages are generic
conversation text. Keep the placeholder label until the corresponding answer
has been verified from an official college source.

## JSON structure

The root JSON object contains:

| Field | Purpose |
| --- | --- |
| `schema_version` | Version of the dataset shape (`1.0`). |
| `dataset_name` | Human-readable dataset title. |
| `college_data_status` | Declares that this is sample-only data. |
| `intents` | Array of intent records. |

Each intent record has:

| Field | Purpose |
| --- | --- |
| `intent` | Unique machine-readable label returned by the classifier/API. |
| `category` | Human-readable topic. |
| `trainable` | Whether patterns are included in classifier training. |
| `response_status` | `placeholder` for unverified college material or `generic` for conversational text. |
| `patterns` | Example questions for this intent. |
| `responses` | Response strings for this intent. The current response service returns the first item. |

The current file has 23 intents, 22 trainable intents, and 92 patterns. Each
intent currently has four patterns. The `fallback` intent has four patterns
for documentation/data validation, but `trainable` is `false`; fallback is
triggered by the classifier/service, not by learning an "unknown" class.

## Intent names

| Intent | Purpose |
| --- | --- |
| `greeting` | Greetings and opening questions. |
| `admission_process` | How to apply for admission. |
| `admission_eligibility` | Questions about entry or program eligibility. |
| `application_documents` | Documents requested during an application. |
| `application_status` | Tracking an admission application. |
| `courses_departments` | Programs, courses, and academic departments. |
| `fees_payment` | Fee information and payment methods. |
| `scholarships` | Scholarships and financial aid. |
| `examinations` | Exam schedules, registration, and rules. |
| `results` | Exam results and grades. |
| `attendance` | Class attendance questions. |
| `placements` | Placement support and activities. |
| `internships` | Student internships. |
| `training_development` | Training and skill development. |
| `campus_facilities` | General campus facilities. |
| `library` | Library services. |
| `hostel` | Hostel accommodation and related questions. |
| `transportation` | College transport services. |
| `contact_information` | How to find official contact channels. |
| `academic_calendar` | Academic and holiday calendar questions. |
| `general_faq` | General student information and FAQs. |
| `goodbye` | Generic conversation closing. |
| `fallback` | Generic response when a question cannot be handled confidently. |

All intents except `fallback` are currently trainable. `greeting` and
`goodbye` use generic responses. Institutional query responses are marked
`placeholder`.

## Adding verified examples or intents

1. Confirm the information and question topic from an authorized, current
   college source before adding a college-specific answer.
2. Add multiple varied `patterns` that express the same intent. Avoid
   duplicates and avoid assigning one question to unrelated intents.
3. Add or edit the `responses` list. Keep unverified institutional responses
   clearly prefixed `SAMPLE PLACEHOLDER:`. The response service currently uses
   only `responses[0]`; additional response entries are not rotated.
4. For a new classifier intent, set `trainable` to `true` and include at least
   three unique patterns. Keep `fallback` non-trainable.
5. If the new label is a required core category, add it to
   `REQUIRED_INTENTS` in `backend/training/validate_dataset.py`.
6. Run validation and tests, then retrain as described below.
7. Review model results and fallback behavior. Adding patterns does not
   guarantee correct predictions.

Do not add real fee amounts, deadlines, eligibility rules, addresses, contact
details, policies, or placement outcomes until independently verified.

## Validation and retraining

From the project root:

```powershell
Set-Location .\backend
.\.venv\Scripts\python.exe -m training.validate_dataset
.\.venv\Scripts\python.exe -m pytest
```

The validator checks required intent coverage, unique intent names, pattern
structure, duplicate patterns after case/punctuation normalization, response
structure, at least three patterns per intent, and that fallback is not
trainable. It uses only Python's standard library.

Train and evaluate the classifier from the backend directory:

```powershell
.\.venv\Scripts\python.exe -m training.train_model
```

The trainer runs a stratified 25% holdout split, prints metrics, and saves the
model fitted only on the training partition to `backend/models/`. The current
split uses 66 training examples and 22 holdout examples. Do not use the
holdout to add patterns or tune the model and then report it as an untouched
evaluation.

See [NLP pipeline](nlp-pipeline.md) for current metrics and limitations.
