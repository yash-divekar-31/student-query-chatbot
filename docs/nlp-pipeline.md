# NLP Pipeline and Model Evaluation

## Processing pipeline

The classifier reads the trainable patterns from
`backend/data/intents.json`. Dataset validation runs before training. Only
intents with `trainable: true` are used; the `fallback` intent is excluded.

### Text preprocessing

`normalize_text` is shared by the vectorizer at training and inference time:

1. Unicode text is normalized with NFKC.
2. Text is lowercased.
3. Punctuation and underscores are replaced with spaces.
4. Repeated whitespace is collapsed and trimmed.

Words and numbers are retained. The project does not remove stop words, stem,
or lemmatize tokens.

### TF-IDF and Logistic Regression

`TfidfVectorizer` uses the `char_wb` analyzer with character n-gram lengths
from 2 through 5, `sublinear_tf=True`, and `normalize_text` as its
preprocessor. Character n-grams can match partial words and spelling
variations, but do not provide semantic understanding.

The vector features are passed to scikit-learn `LogisticRegression` with
`max_iter=1000` and `random_state=42`. The classifier returns the top intent,
its class probability, and probabilities for trained classes internally.
The API response includes the top intent and confidence; it does not expose
the full probability dictionary.

### Training, holdout, and artifacts

There are 22 trainable intents with four patterns each: 88 trainable examples.
`training.train_model` uses a stratified 25% split with `random_state=42`, so
the fixed evaluation uses 66 training examples and 22 holdout examples (one
example for each intent). The holdout patterns are not used to fit the
evaluation model.

The saved artifacts are the classifier fitted on those 66 training examples;
the script deliberately does not refit on the holdout:

- `backend/models/tfidf_vectorizer.joblib`
- `backend/models/logistic_regression.joblib`

FastAPI loads these artifacts once during application startup. Joblib uses
Python serialization: only load model files produced by a trusted local
training run.

## Fallback behavior

The default confidence threshold is `0.065`. A prediction is fallback-eligible
if the query produces no TF-IDF features or if the top class probability is
below this threshold. The response service also uses the dataset fallback
when a predicted label has no response mapping.

The threshold is provisional and not calibrated. Confidence is not a
guarantee that the selected intent is correct. Some valid questions can be
sent to fallback, while some wrong classifications can pass the threshold.

## Evaluation results

The fixed holdout run produced:

| Metric | Result |
| --- | ---: |
| Training examples | 66 |
| Holdout examples | 22 |
| Accuracy | 0.4091 |
| Macro precision | 0.2917 |
| Macro recall | 0.4091 |
| Macro F1 | 0.3212 |

These are top-label classification metrics before fallback response mapping.
There is only one holdout example per intent, so a single example completely
determines each per-intent score. This small, synthetic dataset does not
support a claim of production performance.

For a baseline comparison, a `DummyClassifier(strategy="most_frequent")`
trained on the same 66-example training partition measured 0.0455 accuracy
on the 22-example holdout. The corresponding macro precision was 0.0021,
macro recall 0.0455, and macro F1 0.0040.

The 0.065 threshold accepted 13 of the 22 holdout queries; 6 of those
top-label predictions were correct. A correctly labeled fee question scored
0.0548 and was sent to fallback. A holdout training/development question
scored 0.0655, was classified as `admission_eligibility`, and passed the
threshold incorrectly.

Four-fold out-of-fold development comparisons on this same dataset favored
character n-grams (accuracy 0.5000, macro F1 0.4982) over the initial word
unigram/bigram setup (accuracy 0.1023, macro F1 0.0952). These comparisons
informed feature selection and are not an independent production evaluation.

## Misclassification causes and limitations

- Four patterns per trainable intent are insufficient to represent the range
  of real student wording.
- Several intents share generic wording such as requests for where to find
  information, causing overlapping character features.
- Character n-grams help with surface variations but cannot infer meaning or
  reliably distinguish related topics.
- A 22-example holdout is highly unstable, and confidence is not calibrated.
- The current threshold has both false fallbacks and false accepts.

Collect a much larger set of verified, diverse questions and evaluate it
separately before relying on model decisions. Do not tune against the holdout
and then describe it as an untouched test set.

## Train and evaluate

From the backend directory:

```powershell
.\.venv\Scripts\python.exe -m training.train_model
```

Optional arguments:

```powershell
.\.venv\Scripts\python.exe -m training.train_model `
  --confidence-threshold 0.065 `
  --dataset data\intents.json `
  --model-dir models
```

The command prints the holdout report and writes the two Joblib files to
`models`. See [Dataset guide](dataset-guide.md) for safe dataset edits.
