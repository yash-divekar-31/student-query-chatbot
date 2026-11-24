# Student User Guide

## Start the chatbot

The backend and frontend must both be running. Follow the
[Windows startup instructions in the README](../README.md#run-the-application).
When the page opens, the header shows whether the frontend can reach the
backend's `/health` endpoint.

Open `http://127.0.0.1:5173` in a browser. The chat starts with a welcome
message and suggested questions.

## Ask a question

You can:

- Select one of the suggested questions.
- Type a question into **Ask a student question...** and select **Send**.
- Press **Enter** to submit the current question.

Empty messages are not sent. The input accepts up to 500 characters. The
assistant displays the response returned by the backend; college-related
answers may begin with `SAMPLE PLACEHOLDER:` because official college
information has not been supplied.

Do not enter passwords, account credentials, or other sensitive personal
information. This prototype does not need them to answer a question.

## Understand fallback answers

A message labeled **Fallback response** means the model did not handle the
question confidently, found no matching text features, or had no response for
the predicted intent. Try rephrasing the question or use a suggested topic.
A fallback is not an answer to the original question.

Even a response without a fallback label is only an intent-model result. Check
college-specific facts with an official source, especially while responses
carry the sample placeholder label.

## Conversation history and clearing

Messages remain visible in the current page session so you can follow the
conversation. Select **Clear chat** to return to the welcome message. History
is stored only in browser memory; it is not saved to a database and will not
be restored after a page reload.

## Error messages

- **Cannot reach the chatbot service:** the backend may be stopped or
  unreachable. Ask the project operator to start or check it.
- **Temporarily unavailable:** the backend is running, but it could not load
  its model or dataset.
- **Please enter a valid question:** the input was empty, unsupported, or
  longer than the 500-character limit.
- **Unexpected response / could not process request:** retry later; do not
  rely on a response that was not displayed.

The header's connectivity indicator reflects `/health`; it does not guarantee
that model files are ready for chat requests.
