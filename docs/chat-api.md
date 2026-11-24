# Chat API

## Base URL and routes

For local development, the base URL is `http://127.0.0.1:8000`.

| Method | Path | Purpose |
| --- | --- | --- |
| `GET` | `/health` | Basic HTTP service health response. |
| `POST` | `/chat` | Validate a question, classify its intent, and return a dataset response. |

Swagger UI is available at `http://127.0.0.1:8000/docs`; OpenAPI JSON is at
`http://127.0.0.1:8000/openapi.json`.

## `GET /health`

Successful response (`200`):

```json
{
  "status": "ok",
  "service": "student-query-chatbot"
}
```

This route is a basic process health check. It does not confirm that the model
artifacts or response dataset loaded successfully. If initialization fails,
`POST /chat` returns `503` while `/health` can still return `200`.

## `POST /chat`

Request body:

```json
{
  "question": "How do students pay their fees?"
}
```

The question must be a string from 1 through 500 characters, contain at least
one letter or number after normalization, and be the only top-level request
field. Leading and trailing whitespace is stripped.

Current successful example (`200`, model confidence can change when artifacts
are retrained):

```json
{
  "success": true,
  "question": "How do students pay their fees?",
  "intent": "fees_payment",
  "confidence": 0.1078,
  "response": "SAMPLE PLACEHOLDER: Verified fee amounts and payment instructions are not available. Please use the official fee notice or payment portal. Do not rely on unofficial payment details.",
  "is_fallback": false
}
```

The `response` is read from the dataset. A `SAMPLE PLACEHOLDER:` prefix means
the content is not verified college information.

### Fallback response

Low-confidence, no-feature, or unmapped predictions use the `fallback`
response from the dataset. This is still a successful request (`200`); the
response fields identify it as fallback:

```json
{
  "success": true,
  "question": "xylophonic quasar blorptastic",
  "intent": "fallback",
  "confidence": 0.0537,
  "response": "I am not sure how to help with that yet. Try asking about admissions, courses, fees, exams, student services, placements, or contact information. College-specific details should be confirmed through official sources.",
  "is_fallback": true
}
```

Confidence values above are from the current local model artifact and are
illustrative, not calibrated measures of correctness.

## Errors and validation

| HTTP status | Meaning |
| --- | --- |
| `422` | Invalid request: missing/wrong field, extra field, empty or punctuation-only question, or more than 500 characters. |
| `503` | The model or dataset could not be initialized; the response contains a generic unavailable message. |
| `500` | A caught `RuntimeError` or `ValueError` during request processing returns a generic error detail. Other uncaught server errors use FastAPI's generic HTTP 500 response. |

Errors do not include local file paths or stack traces in the response body.
The frontend converts common errors into student-friendly messages.

The `503` body is:

```json
{
  "detail": "The chatbot is temporarily unavailable. Please try again later."
}
```

Validation errors use FastAPI's standard `{"detail": [...]}` response shape.
The exact entries depend on which field or constraint failed.

## Try it in Swagger or PowerShell

1. Start the backend from the `backend` directory.
2. Open `http://127.0.0.1:8000/docs`.
3. Expand `POST /chat`, choose **Try it out**, enter the JSON request, and
   execute it.

PowerShell example:

```powershell
$body = @{ question = 'How do students pay their fees?' } | ConvertTo-Json
Invoke-RestMethod `
  -Uri 'http://127.0.0.1:8000/chat' `
  -Method Post `
  -ContentType 'application/json' `
  -Body $body
```

See [Testing guide](testing-guide.md) for health and error checks.
