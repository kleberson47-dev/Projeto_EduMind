import type { ReactNode } from 'react'

interface PermissionMiddlewareProps {
  children: ReactNode
}

export function PermissionMiddleware({ children }: PermissionMiddlewareProps) {
  return children
}
