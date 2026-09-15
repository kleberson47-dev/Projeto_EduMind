export const TEMPORARY_MESSAGE_DURATION = 3000

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