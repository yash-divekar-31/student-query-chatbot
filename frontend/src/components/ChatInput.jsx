import { useState } from 'react'

function ChatInput({ onSend, isLoading }) {
  const [value, setValue] = useState('')

  const submit = (event) => {
    event.preventDefault()
    if (!value.trim()) return

    onSend(value)
    setValue('')
  }

  return (
    <form className="chat-input" onSubmit={submit}>
      <input
        className="chat-input__field"
        type="text"
        value={value}
        onChange={(event) => setValue(event.target.value)}
        placeholder="Ask a student question..."
        aria-label="Student question"
        maxLength={500}
        disabled={isLoading}
      />
      <button
        className="chat-input__send"
        type="submit"
        disabled={isLoading || !value.trim()}
      >
        Send
      </button>
    </form>
  )
}

export default ChatInput
