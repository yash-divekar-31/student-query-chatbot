# Testing Guide

Run the commands from the project root unless a step changes directory.
`backend/.venv` and `frontend/node_modules` must already be installed.

## Backend tests

```powershell
Set-Location .\backend
.\.venv\Scripts\python.exe -m pytest
```

The current suite contains 53 tests covering dataset validation,
preprocessing, classifier training/prediction, response mapping, health, and
the chat API. A Starlette/httpx deprecation warning may appear from the
installed TestClient integration; it does not fail the suite.

## Dataset validation

From the backend directory:

```powershell
.\.venv\Scripts\python.exe -m training.validate_dataset
```

Expected current summary:

```text
Dataset is valid: 23 intents, 22 trainable intents, 92 patterns.
```

## Python compilation

From the backend directory:

```powershell
.\.venv\Scripts\python.exe -m compileall -q app training tests
```

No output and exit code `0` indicates successful compilation.

## Frontend tests, lint, and production build

From the frontend directory:

```powershell
npm test
npm run lint
npm run build
```

`npm test` uses Node.js's built-in test runner and currently contains 7 API
client tests. `npm run lint` runs oxlint. `npm run build` runs the Vite
production build and writes generated files to `frontend/dist`.

## Live API checks

Start Uvicorn in one terminal, then use another PowerShell terminal:

```powershell
Invoke-RestMethod -Uri 'http://127.0.0.1:8000/health'

$body = @{ question = 'How do students pay their fees?' } | ConvertTo-Json
Invoke-RestMethod `
  -Uri 'http://127.0.0.1:8000/chat' `
  -Method Post `
  -ContentType 'application/json' `
  -Body $body
```

Open `http://127.0.0.1:8000/docs` to try the endpoints through Swagger UI.
The backend tests also cover invalid payloads, the 500-character input limit,
fallback behavior, and missing model artifacts.

## Live frontend check

With the backend running, start Vite in a separate terminal and open
`http://127.0.0.1:5173`. Submit a question, check the dataset-backed reply,
submit an unknown query to see fallback labeling, then clear the chat. The
frontend Node tests cover API requests, response validation, network failures,
422/503 handling, and fallback metadata.

The last full verification recorded 53 backend tests and 7 frontend tests
passing, dataset validation and compilation succeeding, and frontend lint and
production build succeeding. Model evaluation figures are reported separately
in [NLP pipeline](nlp-pipeline.md).
