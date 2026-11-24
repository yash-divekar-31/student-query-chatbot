function formatTime(timestamp) {
  return new Intl.DateTimeFormat(undefined, {
    hour: '2-digit',
    minute: '2-digit',
  }).format(timestamp)
}

function ChatMessage({ message }) {
  return (
    <article className={`message message--${message.role}`}>
      {message.isFallback && (
        <span className="message__fallback-label">Fallback response</span>
      )}
      <p className="message__bubble">{message.text}</p>
      <time className="message__time" dateTime={message.timestamp.toISOString()}>
        {formatTime(message.timestamp)}
      </time>
    </article>
  )
}

export default ChatMessage
