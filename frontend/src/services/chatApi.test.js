import assert from 'node:assert/strict'
import { afterEach, test } from 'node:test'

import { sendChatMessage } from './chatApi.js'

const originalFetch = globalThis.fetch

afterEach(() => {
  globalThis.fetch = originalFetch
})

test('sends the trimmed question and returns the actual API response', async () => {
  const apiBody = {
    success: true,
    question: 'Where can I find the tuition fees?',
    intent: 'fees_payment',
    confidence: 0.095,
    response: 'SAMPLE PLACEHOLDER: Check official fee information.',
    is_fallback: false,
  }
  let requestUrl
  let requestOptions

  globalThis.fetch = async (url, options) => {
    requestUrl = url
    requestOptions = options
    return {
      ok: true,
      json: async () => apiBody,
    }
  }

  const result = await sendChatMessage('  Where can I find the tuition fees?  ')

  assert.equal(requestUrl, 'http://127.0.0.1:8000/chat')
  assert.equal(requestOptions.method, 'POST')
  assert.equal(requestOptions.headers['Content-Type'], 'application/json')
  assert.deepEqual(JSON.parse(requestOptions.body), {
    question: 'Where can I find the tuition fees?',
  })
  assert.equal(result, apiBody)
})

test('does not make a request for empty questions', async () => {
  let requestMade = false
  globalThis.fetch = async () => {
    requestMade = true
    throw new Error('fetch should not be called')
  }

  await assert.rejects(sendChatMessage('  '), {
    name: 'ChatApiError',
    message: 'Please enter a question before sending.',
  })
  assert.equal(requestMade, false)
})

test('turns HTTP 422 into a student-friendly validation message', async () => {
  globalThis.fetch = async () => ({
    ok: false,
    status: 422,
  })

  await assert.rejects(sendChatMessage('?!'), {
    name: 'ChatApiError',
    status: 422,
    message: 'Please enter a valid question using up to 500 characters.',
  })
})

test('turns HTTP 503 into a student-friendly availability message', async () => {
  globalThis.fetch = async () => ({
    ok: false,
    status: 503,
  })

  await assert.rejects(sendChatMessage('Question'), {
    name: 'ChatApiError',
    status: 503,
    message: 'The chatbot is temporarily unavailable. Please try again later.',
  })
})

test('hides technical details for an unexpected API response', async () => {
  globalThis.fetch = async () => ({
    ok: true,
    json: async () => ({ detail: 'internal stack trace' }),
  })

  await assert.rejects(sendChatMessage('Question'), {
    name: 'ChatApiError',
    message: 'The chatbot returned an unexpected response. Please try again.',
  })
})

test('converts network failures into a friendly service message', async () => {
  globalThis.fetch = async () => {
    throw new TypeError('Failed to fetch')
  }

  await assert.rejects(sendChatMessage('Question'), {
    name: 'ChatApiError',
    isNetworkError: true,
    message:
      'Cannot reach the chatbot service. Check that the backend is running and try again.',
  })
})

test('preserves fallback metadata from the API response', async () => {
  const fallbackBody = {
    success: true,
    question: 'unrecognized query',
    intent: 'fallback',
    confidence: 0.05,
    response: 'Please try another question.',
    is_fallback: true,
  }
  globalThis.fetch = async () => ({
    ok: true,
    json: async () => fallbackBody,
  })

  const result = await sendChatMessage('unrecognized query')

  assert.equal(result.is_fallback, true)
  assert.equal(result.response, fallbackBody.response)
})
