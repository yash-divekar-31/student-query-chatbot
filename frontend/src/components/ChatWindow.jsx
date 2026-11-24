import { useEffect, useRef } from 'react'
import ChatMessage from './ChatMessage'
import SuggestedQuestions from './SuggestedQuestions'

function ChatWindow({ messages, isLoading, onSuggestedQuestion }) {
  const endRef = useRef(null)

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, isLoading])

  const showSuggestions = messages.length === 1

  return (
    <section className="chat-window" aria-live="polite">
      <div className="message-list">
        {messages.map((message) => (
          <ChatMessage key={message.id} message={message} />
        ))}

        {showSuggestions && (
          <SuggestedQuestions
            onSelect={onSuggestedQuestion}
            disabled={isLoading}
          />
        )}

        {isLoading && (
          <div className="loading-indicator" aria-label="Waiting for a response">
            <span />
            <span />
            <span />
          </div>
        )}

        <div ref={endRef} />
      </div>
    </section>
  )
}

export default ChatWindow
