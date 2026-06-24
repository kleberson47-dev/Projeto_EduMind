import type { ReactNode } from 'react'

interface SidebarLayoutProps {
  children?: ReactNode
}

export function SidebarLayout({ children }: SidebarLayoutProps) {
  return children ?? null
}
