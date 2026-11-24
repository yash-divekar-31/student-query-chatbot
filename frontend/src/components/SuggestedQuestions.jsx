const suggestedQuestions = [
  'What is the admission process?',
  'Which courses are available?',
  'How can I find fee information?',
  'What student facilities are available?',
]

function SuggestedQuestions({ onSelect, disabled }) {
  return (
    <div className="suggestions" aria-label="Suggested questions">
      {suggestedQuestions.map((question) => (
        <button
          className="suggestion-button"
          type="button"
          key={question}
          onClick={() => onSelect(question)}
          disabled={disabled}
        >
          {question}
        </button>
      ))}
    </div>
  )
}

export default SuggestedQuestions
