export const TEMPORARY_MESSAGE_DURATION = 3000
export const TEMPORARY_MESSAGE_STORAGE_KEY = 'temporary-message'

export type TemporaryMessageType = 'success' | 'error'

export interface TemporaryMessage {
  type: TemporaryMessageType
  text: string
}

export function createTemporaryMessage(
  type: TemporaryMessageType,
  text: string,
): TemporaryMessage {
  return { type, text }
}

export function saveTemporaryMessageAfterReload(message: TemporaryMessage): void {
  sessionStorage.setItem(TEMPORARY_MESSAGE_STORAGE_KEY, JSON.stringify(message))
}

export function readTemporaryMessageAfterReload(): TemporaryMessage | null {
  const rawMessage = sessionStorage.getItem(TEMPORARY_MESSAGE_STORAGE_KEY)

  if (!rawMessage) {
    return null
  }

  sessionStorage.removeItem(TEMPORARY_MESSAGE_STORAGE_KEY)

  try {
    const message = JSON.parse(rawMessage) as TemporaryMessage

    if (message && typeof message.type === 'string' && typeof message.text === 'string') {
      return message
    }
  } catch {
    return null
  }

  return null
}