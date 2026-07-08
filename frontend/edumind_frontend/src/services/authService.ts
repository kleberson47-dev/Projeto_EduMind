import type {
  AuthTokens,
  LoginRequest,
  RefreshTokenRequest,
  RefreshTokenResponse,
} from '../models/Auth'
import { API_ENDPOINTS } from '../utils/api'
import { requestJson } from '../utils/requests'

export async function login(payload: LoginRequest): Promise<AuthTokens> {
  return requestJson<AuthTokens>(API_ENDPOINTS.accounts.token, {
    method: 'POST',
    body: payload,
  })
}

export async function refreshAccessToken(
  payload: RefreshTokenRequest,
): Promise<RefreshTokenResponse> {
  return requestJson<RefreshTokenResponse>(API_ENDPOINTS.accounts.refreshToken, {
    method: 'POST',
    body: payload,
  })
}
