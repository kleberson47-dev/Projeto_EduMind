import { Suspense, lazy } from 'react'
import type { ComponentType } from 'react'
import { Navigate, createBrowserRouter } from 'react-router-dom'

import { SuspenseLoader } from './components/SuspenseLoader/index'
import { BaseLayout } from './layouts/BaseLayout'
import { SidebarLayout } from './layouts/SidebarLayout'
import { AuthMiddleware } from './middlewares/AuthMiddleware'

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
const IndexAlunoPage = loader(lazy(() => import('./content/pages/IndexAlunoPage')))
const EditarPerfilPage = loader(lazy(() => import('./content/pages/EditarPerfil')))

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
        path: 'app',
        element: (
          <AuthMiddleware>
            <SidebarLayout />
          </AuthMiddleware>
        ),
        children: [
          {
            index: true,
            element: <IndexAlunoPage />,
          },
          {
            path: 'inicio_aluno',
            element: <IndexAlunoPage />,
          },
          {
            path: 'editar-perfil',
            element: <EditarPerfilPage />,
          },
        ],
      },
      {
        path: '*',
        element: <Navigate to="/login" replace />,
      },
    ],
  },
])
