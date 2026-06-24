export interface AuthState {
  token: string | null
  isAuthenticated: boolean
}

export const initialAuthState: AuthState = {
  token: null,
  isAuthenticated: false,
}
