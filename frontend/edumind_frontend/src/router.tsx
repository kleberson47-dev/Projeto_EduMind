export interface AppRoute {
  path: string
  element?: unknown
  children?: AppRoute[]
}

export const appRoutes: AppRoute[] = []
