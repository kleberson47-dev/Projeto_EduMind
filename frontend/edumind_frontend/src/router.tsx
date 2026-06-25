import { Suspense, lazy } from 'react'
import type { ComponentType } from 'react'
import { Navigate, createBrowserRouter } from 'react-router-dom'

import { SuspenseLoader } from './components/SuspenseLoader/index'
import { BaseLayout } from './layouts/BaseLayout'

function loader<T extends object>(Component: ComponentType<T>) {
  return function LoadedComponent(props: T) {
    return (
      <Suspense fallback={<SuspenseLoader />}>
        <Component {...props} />
      </Suspense>
    )
  }
}

const LoginPage = loader(
  lazy(() =>
    import('./content/pages/Login').then((module) => ({
      default: module.LoginPage,
    })),
  ),
)
const CriarContaPage = loader(lazy(() => import('./content/pages/CriarConta')))
const EsqueceuSenhaPage = loader(lazy(() => import('./content/pages/EsqueceuSenha')))

export const appRouter = createBrowserRouter([
  {
    path: '/',
    element: <BaseLayout />,
    children: [
      {
        index: true,
        element: <Navigate to="/login" replace />,
      },
      {
        path: 'login',
        element: <LoginPage />,
      },
      {
        path: 'criar-conta',
        element: <CriarContaPage />,
      },
      {
        path: 'esqueceu-senha',
        element: <EsqueceuSenhaPage />,
      },
      {
        path: '*',
        element: <Navigate to="/login" replace />,
      },
    ],
  },
])
