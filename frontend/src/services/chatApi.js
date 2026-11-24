const API_BASE_URL =
  (import.meta.env?.VITE_API_BASE_URL || 'http://127.0.0.1:8000').replace(
    /\/+$/,
    '',
  )

const NETWORK_ERROR_MESSAGE =
  'Cannot reach the chatbot service. Check that the backend is running and try again.'
const INVALID_RESPONSE_MESSAGE =
  'The chatbot returned an unexpected response. Please try again.'

export class ChatApiError extends Error {
  constructor(message, { status = null, isNetworkError = false } = {}) {
    super(message)
    this.name = 'ChatApiError'
    this.status = status
    this.isNetworkError = isNetworkError
  }
}

async function request(url, options) {
  try {
    return await fetch(url, options)
  } catch (error) {
    if (error instanceof TypeError) {
      throw new ChatApiError(NETWORK_ERROR_MESSAGE, { isNetworkError: true })
    }

    throw error
  }
}

async function readJson(response) {
  try {
    return await response.json()
  } catch (error) {
    if (error instanceof SyntaxError || error instanceof TypeError) {
      throw new ChatApiError(INVALID_RESPONSE_MESSAGE)
    }

    throw error
  }
}

function httpError(status) {
  if (status === 422) {
    return new ChatApiError(
      'Please enter a valid question using up to 500 characters.',
      { status },
    )
  }

  if (status === 503) {
    return new ChatApiError(
      'The chatbot is temporarily unavailable. Please try again later.',
      { status },
    )
  }

  return new ChatApiError(
    'The chatbot could not process your request. Please try again later.',
    { status },
  )
}

export async function checkHealth() {
  const response = await request(`${API_BASE_URL}/health`)

  if (!response.ok) {
    throw httpError(response.status)
  }

  const body = await readJson(response)
  if (!body || body.status !== 'ok') {
    throw new ChatApiError(INVALID_RESPONSE_MESSAGE)
  }

  return body
}

export async function sendChatMessage(question) {
  if (typeof question !== 'string' || !question.trim()) {
    throw new ChatApiError('Please enter a question before sending.')
  }

  const response = await request(`${API_BASE_URL}/chat`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ question: question.trim() }),
  })

  if (!response.ok) {
    throw httpError(response.status)
  }

  const body = await readJson(response)
  if (
    !body ||
    body.success !== true ||
    typeof body.question !== 'string' ||
    typeof body.intent !== 'string' ||
    !body.intent.trim() ||
    typeof body.confidence !== 'number' ||
    !Number.isFinite(body.confidence) ||
    body.confidence < 0 ||
    body.confidence > 1 ||
    typeof body.response !== 'string' ||
    !body.response.trim() ||
    typeof body.is_fallback !== 'boolean'
  ) {
    throw new ChatApiError(INVALID_RESPONSE_MESSAGE)
  }

  return body
}
