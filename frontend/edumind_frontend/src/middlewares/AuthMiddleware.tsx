import { useEffect, useState } from 'react'
import type { ReactNode } from 'react'
import { Navigate, Outlet, useLocation } from 'react-router-dom'

import { SuspenseLoader } from '../components/SuspenseLoader/index'
import {
  clearAuthSession,
  getAccessToken,
  getRefreshToken,
  isTokenExpired,
  saveRedirectAfterLogin,
  setAuthSession,
} from '../features/auth'
import { refreshAccessToken } from '../services'

interface AuthMiddlewareProps {
  children?: ReactNode
}

export function AuthMiddleware({ children }: AuthMiddlewareProps) {
  const location = useLocation()
  const [isCheckingSession, setIsCheckingSession] = useState(true)
  const [isAllowed, setIsAllowed] = useState(false)

  useEffect(() => {
    let isMounted = true

    async function validateSession() {
      const pathToReturn = `${location.pathname}${location.search}${location.hash}`
      const accessToken = getAccessToken()

      if (accessToken && !isTokenExpired(accessToken)) {
        if (isMounted) {
          setIsAllowed(true)
          setIsCheckingSession(false)
        }
        return
      }

      const refreshToken = getRefreshToken()
      if (!refreshToken) {
        saveRedirectAfterLogin(pathToReturn)
        clearAuthSession()
        if (isMounted) {
          setIsAllowed(false)
          setIsCheckingSession(false)
        }
        return
      }

      try {
        const newAccess = await refreshAccessToken({ refresh: refreshToken })
        setAuthSession({ access: newAccess.access, refresh: refreshToken })
        if (isMounted) {
          setIsAllowed(true)
          setIsCheckingSession(false)
        }
      } catch {
        saveRedirectAfterLogin(pathToReturn)
        clearAuthSession()
        if (isMounted) {
          setIsAllowed(false)
          setIsCheckingSession(false)
        }
      }
    }

    const interval = window.setInterval(() => {
      void validateSession()
    }, 30000)

    void validateSession()

    return () => {
      isMounted = false
      window.clearInterval(interval)
    }
  }, [location.hash, location.pathname, location.search])

  if (isCheckingSession) {
    return <SuspenseLoader />
  }

  if (!isAllowed) {
    return <Navigate to="/login" replace state={{ from: location }} />
  }

  return children ?? <Outlet />
}
