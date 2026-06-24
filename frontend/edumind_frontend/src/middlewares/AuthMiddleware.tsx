import type { ReactNode } from 'react'

interface AuthMiddlewareProps {
  children: ReactNode
}

export function AuthMiddleware({ children }: AuthMiddlewareProps) {
  return children
}
