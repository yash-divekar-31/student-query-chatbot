import { useEffect, useRef, useState } from 'react'
import ChatHeader from './components/ChatHeader'
import ChatWindow from './components/ChatWindow'
import ChatInput from './components/ChatInput'
import {
  ChatApiError,
  checkHealth,
  sendChatMessage,
} from './services/chatApi'
import './App.css'

function App() {
  const [messages, setMessages] = useState([
    {
      id: 'welcome',
      role: 'assistant',
      text: 'Hello! I am ready to help with your student queries.',
      timestamp: new Date(),
    },
  ])
  const [isLoading, setIsLoading] = useState(false)
  const [backendStatus, setBackendStatus] = useState('checking')
  const messageCounter = useRef(1)

  useEffect(() => {
    let isMounted = true

    checkHealth()
      .then(() => {
        if (isMounted) setBackendStatus('online')
      })
      .catch(() => {
        if (isMounted) setBackendStatus('offline')
      })

    return () => {
      isMounted = false
    }
  }, [])

  const clearChat = () => {
    setMessages([
      {
        id: `welcome-${Date.now()}`,
        role: 'assistant',
        text: 'Hello! I am ready to help with your student queries.',
        timestamp: new Date(),
      },
    ])
  }

  const submitMessage = async (text) => {
    const trimmedText = text.trim()
    if (!trimmedText || isLoading) return

    const userMessage = {
      id: `message-${messageCounter.current++}`,
      role: 'user',
      text: trimmedText,
      timestamp: new Date(),
    }

    setMessages((current) => [...current, userMessage])
    setIsLoading(true)

    try {
      const response = await sendChatMessage(trimmedText)
      setBackendStatus('online')
      setMessages((current) => [
        ...current,
        {
          id: `message-${messageCounter.current++}`,
          role: 'assistant',
          text: response.response,
          isFallback: response.is_fallback,
          timestamp: new Date(),
        },
      ])
    } catch (error) {
      setMessages((current) => [
        ...current,
        {
          id: `message-${messageCounter.current++}`,
          role: 'error',
          text: error instanceof ChatApiError
            ? error.message
            : 'The chatbot could not process your request. Please try again later.',
          timestamp: new Date(),
        },
      ])
      if (
        error instanceof ChatApiError &&
        (error.isNetworkError || error.status === 503)
      ) {
        setBackendStatus('offline')
      }
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <main className="app-shell">
      <section className="chat-card" aria-label="Student query chatbot">
        <ChatHeader
          backendStatus={backendStatus}
          onClearChat={clearChat}
          isLoading={isLoading}
        />
        <ChatWindow
          messages={messages}
          isLoading={isLoading}
          onSuggestedQuestion={submitMessage}
        />
        <ChatInput onSend={submitMessage} isLoading={isLoading} />
      </section>
    </main>
  )
}

export default App
