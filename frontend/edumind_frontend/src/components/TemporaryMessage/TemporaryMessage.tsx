import type { TemporaryMessage as TemporaryMessageData } from '../../utils'

import './TemporaryMessage.css'

interface TemporaryMessageProps {
  message: TemporaryMessageData | null
}

export function TemporaryMessage({ message }: TemporaryMessageProps) {
  if (!message) {
    return null
  }

  return (
    <div
      className={`temporary-message temporary-message-${message.type}`}
      role="status"
    >
      <span>{message.text}</span>
      <span className="temporary-message-progress" aria-hidden="true" />
    </div>
  )
}