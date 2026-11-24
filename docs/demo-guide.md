# Project Demonstration Guide

## Pre-demo checklist

- Install the backend requirements and frontend packages before the
  presentation; do not make package installation part of the live demo.
- Confirm both Joblib files exist in `backend/models/`.
- Start Uvicorn and Vite in separate terminals. Confirm the page opens and
  `GET /health` responds. Also submit one question because `/health` does not
  prove that model files are ready.
- Check that the browser uses the configured local API URL and that ports
  `8000` and `5173` are available.
- Keep the sample-data notice and actual evaluation metrics ready to show.
- Use only the sample questions below; do not enter credentials or personal
  information.
- Reset the conversation with **Clear chat** before beginning.
- If live services fail, explain the error accurately rather than implying
  deployment or production readiness.

## Demonstration sequence

1. **Introduce the project.** Explain that this is a student-query chatbot
   prototype using a local sample intent dataset. Emphasize that the
   institution-specific answers are placeholders.
2. **Explain the architecture.** Show
   [system-architecture.md](system-architecture.md): React/Vite calls a
   FastAPI API; the backend classifies intents and maps them to JSON responses.
3. **Start the backend.** In PowerShell from the project root:

   ```powershell
   Set-Location .\backend
   .\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
   ```

4. **Start the frontend.** In another PowerShell terminal from the project
   root:

   ```powershell
   Set-Location .\frontend
   npm run dev -- --host 127.0.0.1
   ```

5. **Demonstrate common questions.** Open `http://127.0.0.1:5173`, ask
   `How do students pay their fees?`, and show that the backend returns the
   configured fees response with its `SAMPLE PLACEHOLDER:` label. Try a
   suggested question and explain that the response comes from the JSON data,
   not a generative model.
6. **Show fallback.** Submit `xylophonic quasar blorptastic`. Explain the
   visible fallback label and that students should rephrase or check official
   sources.
7. **Show history and clear chat.** Submit more than one query to show
   session-only history, then select **Clear chat**.
8. **Explain NLP.** Open `docs/nlp-pipeline.md`. Describe normalization,
   character n-gram TF-IDF, Logistic Regression, and threshold-based fallback.
9. **Show testing and evaluation.** Run the commands in
   [testing-guide.md](testing-guide.md), then report the actual 22-example
   holdout metrics: accuracy `0.4091`, macro precision `0.2917`, macro recall
   `0.4091`, and macro F1 `0.3212`.
10. **Discuss limits and future scope.** State that this is synthetic sample
    data with only four patterns per trainable intent, not verified college
    information and not production-accurate. Future work requires verified
    responses and a larger independent evaluation set.

## Seven-minute presentation script

| Time | Talking points and action |
| --- | --- |
| 0:00-0:45 | **Problem:** Students need a simple way to ask common questions. This prototype demonstrates intent classification and dataset-backed answers; it does not contain official college data. |
| 0:45-1:30 | **Objectives and stack:** Explain the React/Vite interface, FastAPI service, JSON intent data, TF-IDF features, Logistic Regression, and Joblib artifacts. State that there is no database or LLM integration. |
| 1:30-2:15 | **Architecture:** Show the browser-to-API flow and the backend's startup model loading, classifier, response map, and fallback. Point out that `/health` is a basic health check. |
| 2:15-4:15 | **Live demonstration:** Ask `How do students pay their fees?` and show the `SAMPLE PLACEHOLDER:` response. Ask `xylophonic quasar blorptastic` and show the fallback label. Submit another question to show history, then clear the chat. |
| 4:15-5:15 | **NLP:** Describe NFKC normalization, lowercase/punctuation/whitespace handling, `char_wb` character n-grams from 2 to 5, TF-IDF, and Logistic Regression. Explain the `0.065` provisional threshold. |
| 5:15-6:00 | **Evaluation:** Report 66 training and 22 holdout examples and all four metrics. Explain that there is one holdout example per intent and the results are not a production estimate. |
| 6:00-7:00 | **Limitations and future work:** Emphasize synthetic patterns, placeholders, low measured performance, and uncalibrated confidence. Propose verified content, more diverse student questions, and independent evaluation before deployment. |

## Possible examiner or interviewer questions

### What is an intent?

An intent is a label for the kind of question, such as `fees_payment` or
`library`. The classifier predicts one of the trainable labels.

### Why is the dataset separate from application code?

It lets maintainers update question patterns and responses without editing the
API or UI. Changes should be validated and the model retrained when trainable
patterns change.

### Why use TF-IDF?

TF-IDF converts text into numeric features based on character n-gram
frequency. Logistic Regression can use those features to classify the
question. TF-IDF itself does not understand meaning.

### Is this chatbot generative AI?

No. It uses TF-IDF features and Logistic Regression to classify an intent,
then returns a predefined response from the JSON dataset. It does not call an
LLM or generate new response text.

### Why use character n-grams?

The vectorizer uses `char_wb` character n-grams of length 2-5. They can
capture some partial-word and spelling variation. Development comparisons on
the current tiny dataset favored them over the initial word unigram/bigram
configuration, but they do not provide semantic understanding.

### What does the confidence value mean?

It is the highest Logistic Regression class probability for that question.
It is not a calibrated guarantee that the predicted intent is correct. The
configured threshold is `0.065`; low scores can trigger fallback.

### What is the measured accuracy?

The fixed holdout had 22 examples, one per trainable intent. Accuracy was
`0.4091`, macro precision `0.2917`, macro recall `0.4091`, and macro F1
`0.3212`. These small synthetic-data metrics are not a production estimate.

### How is the fallback selected?

The fallback is returned when the vectorizer finds no features, the top
probability is below the threshold, or there is no response mapping for the
predicted label. The fallback itself is a generic response in the JSON file
and is not a trained classifier class.

### Where are answers stored? Is there a database?

Intent patterns and response strings are stored in
`backend/data/intents.json`. The project has no database. Conversation history
is held only in the frontend's in-memory React state.

### How can college information be made official?

Replace placeholders only with information verified against current official
college sources, add reviewed question patterns, run dataset validation and
tests, retrain, and evaluate against a separate set of student questions.
Never infer fees, dates, eligibility, policies, contacts, or placement
statistics.

### Does `/health` verify that the classifier is ready?

No. It verifies the basic HTTP health route. If model initialization fails,
`/health` can still return `200`, while `POST /chat` returns `503`.

### How does the application avoid using the holdout examples for fitting?

The training script makes a stratified split first, fits the vectorizer and
classifier on the 66-example training partition, evaluates on the 22-example
holdout, and saves that training-only fitted model. The saved model was also
compared with a fresh in-memory fit on that partition.

### Why is the reported holdout accuracy low?

There are only four synthetic patterns per trainable intent and one example
per intent in the holdout. Similar wording across intents and the limited
coverage of real student phrasing make classification difficult. The result
should be reported as measured, not improved by tuning on the holdout.

### What do macro precision, recall, and F1 summarize?

They compute a metric per intent and average the intent scores equally.
Macro averaging prevents larger classes from dominating, but each class has
only one holdout example here, so these numbers are highly unstable.

### What does a confidence score represent?

It is the highest Logistic Regression class probability for the query. It is
not the model's measured accuracy and is not calibrated as a guarantee that a
prediction is correct.

### Why is the fallback intent not trained?

Unknown questions cannot be completely represented by a finite list of
patterns. The fallback label is selected by the service when there are no
features, confidence is below the threshold, or no response mapping exists.

### What validation does the API perform?

`POST /chat` requires a string question of at most 500 characters, rejects
empty or punctuation-only content, and forbids extra top-level fields. Invalid
requests receive HTTP `422`.

### What happens if a model artifact is missing?

The app's startup initialization leaves the chat service unavailable.
`POST /chat` returns HTTP `503` with a generic message; it does not return a
local path or traceback. `/health` can still return `200`.

### How are responses chosen?

The classifier's predicted intent is used to look up that intent in
`intents.json`. The service returns the first response in its `responses`
array. Low-confidence or unmapped predictions use the first fallback response.

### Is chat history stored after closing or reloading the page?

No. Messages are stored in React state for the current page session. There is
no database or server-side conversation storage.

### How does the frontend know where the backend is?

The Vite client reads `VITE_API_BASE_URL` from `frontend/.env` and appends
`/health` or `/chat`. The local configuration points to
`http://127.0.0.1:8000`.

### How are cross-origin requests restricted?

FastAPI CORS middleware allows the configured local Vite origins
(`localhost:5173` and `127.0.0.1:5173`) and only the configured `GET` and
`POST` methods. This local configuration is not a production deployment
policy.

### How can a new intent be added?

Add a JSON intent object with a unique label, category, trainability flag,
response status, at least three unique patterns, and non-empty responses.
Update `REQUIRED_INTENTS` if it is a new required core category. Run dataset
validation and tests, then retrain and evaluate.

### Why use Joblib?

The project serializes the fitted scikit-learn vectorizer and Logistic
Regression model to local files so FastAPI can load them at startup. Only
artifacts from a trusted training run should be loaded.

### What tests are included?

The backend uses pytest and FastAPI TestClient for dataset validation,
preprocessing, classifier behavior, response mapping, health, and API
validation. The frontend uses Node's built-in test runner for API request and
error handling. oxlint and Vite build scripts are also available.

### Is the project production-ready or deployed?

No. It is a locally run prototype. The sample dataset is unverified, the
holdout metrics are weak and unstable, and deployment, monitoring, privacy
review, and production security have not been completed.
