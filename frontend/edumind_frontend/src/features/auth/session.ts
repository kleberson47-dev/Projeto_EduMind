import type { AuthTokens } from '../../models/Auth'
import {
  AUTH_REDIRECT_STORAGE_KEY,
  AUTH_REFRESH_STORAGE_KEY,
} from '../../utils/auth'

interface JwtPayload {
  exp?: number
}

let accessTokenInMemory: string | null = null

function decodeJwtPayload(token: string): JwtPayload | null {
  try {
    const payloadBase64 = token.split('.')[1]
    if (!payloadBase64) {
      return null
    }

    const normalized = payloadBase64.replace(/-/g, '+').replace(/_/g, '/')
    const padded = normalized.padEnd(Math.ceil(normalized.length / 4) * 4, '=')
    return JSON.parse(window.atob(padded)) as JwtPayload
  } catch {
    return null
  }
}

export function setAuthSession(tokens: AuthTokens): void {
  accessTokenInMemory = tokens.access
  window.sessionStorage.setItem(AUTH_REFRESH_STORAGE_KEY, tokens.refresh)
}

export function clearAuthSession(): void {
  accessTokenInMemory = null
  window.sessionStorage.removeItem(AUTH_REFRESH_STORAGE_KEY)
}

export function getAccessToken(): string | null {
  return accessTokenInMemory
}

export function getRefreshToken(): string | null {
  return window.sessionStorage.getItem(AUTH_REFRESH_STORAGE_KEY)
}

export function isTokenExpired(token: string, thresholdInSeconds = 20): boolean {
  const payload = decodeJwtPayload(token)
  if (!payload?.exp) {
    return true
  }

  const currentTimestamp = Math.floor(Date.now() / 1000)
  return payload.exp <= currentTimestamp + thresholdInSeconds
}

export function saveRedirectAfterLogin(path: string): void {
  window.sessionStorage.setItem(AUTH_REDIRECT_STORAGE_KEY, path)
}

export function consumeRedirectAfterLogin(): string | null {
  const storedPath = window.sessionStorage.getItem(AUTH_REDIRECT_STORAGE_KEY)
  if (!storedPath) {
    return null
  }

  window.sessionStorage.removeItem(AUTH_REDIRECT_STORAGE_KEY)
  return storedPath
}
