import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'

import type { User } from '../../models'
import { getCurrentUser } from '../../services'
import { clearAuthSession, getAccessToken } from '../../features/auth'

import './Index.css'

export default function IndexPage() {
  const navigate = useNavigate()
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [errorMessage, setErrorMessage] = useState<string | null>(null)

  useEffect(() => {
    async function loadCurrentUser() {
      const token = getAccessToken()
      if (!token) {
        setErrorMessage('Sessao nao encontrada. Faca login novamente.')
        setIsLoading(false)
        return
      }

      try {
        const profile = await getCurrentUser(token)
        setUser(profile)
      } catch {
        setErrorMessage('Nao foi possivel carregar os dados do usuario.')
      } finally {
        setIsLoading(false)
      }
    }

    void loadCurrentUser()
  }, [])

  const handleLogout = () => {
    clearAuthSession()
    navigate('/login', { replace: true })
  }

  const handleEditProfile = () => {
    navigate('/app/editar-perfil')
  }

  return (
    <section className="index-page" aria-label="Tela inicial do sistema">
      <header className="index-header">
        <h1>Painel inicial</h1>
        <button type="button" className="logout-button" onClick={handleLogout}>
          Sair
        </button>
      </header>

      <article className="index-card">
        <div className="index-card-header">
          <h2>Bem-vindo ao EduMind</h2>
          <button type="button" className="edit-button" onClick={handleEditProfile}>
            Editar
          </button>
        </div>

        {isLoading && <p>Carregando dados da conta...</p>}

        {!isLoading && errorMessage && <p className="index-error">{errorMessage}</p>}

        {!isLoading && !errorMessage && user && (
          <ul className="index-user-list">
            <li>
              <strong>Nome:</strong> {user.nome}
            </li>
            <li>
              <strong>Email:</strong> {user.email}
            </li>
            <li>
              <strong>Perfil:</strong> {user.role}
            </li>
          </ul>
        )}
      </article>
    </section>
  )
}
