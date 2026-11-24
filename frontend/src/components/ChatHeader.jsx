function ChatHeader({ backendStatus, onClearChat, isLoading }) {
  const statusText =
    backendStatus === 'online'
      ? 'Backend connected'
      : backendStatus === 'offline'
        ? 'Backend unavailable'
        : 'Checking backend'

  return (
    <header className="chat-header">
      <div className="chat-header__identity">
        <div className="chat-header__avatar" aria-hidden="true">
          SQ
        </div>
        <div>
          <h1>Student Query Assistant</h1>
          <div className="chat-header__status" role="status">
            <span
              className={`status-dot status-dot--${backendStatus}`}
              aria-hidden="true"
            />
            {statusText}
          </div>
        </div>
      </div>

      <div className="chat-header__actions">
        <button
          className="clear-button"
          type="button"
          onClick={onClearChat}
          disabled={isLoading}
        >
          Clear chat
        </button>
      </div>
    </header>
  )
}

export default ChatHeader
