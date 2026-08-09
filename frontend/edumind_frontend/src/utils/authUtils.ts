import type { AuthTokens, LoginRequest } from '../models/Auth'
import { API_ENDPOINTS } from './api'
import { requestJson } from './requests'

export async function getAuthTokens(payload: LoginRequest): Promise<AuthTokens> {
  return requestJson<AuthTokens>(API_ENDPOINTS.accounts.token, {
    method: 'POST',
    body: payload,
  })
}
