import { useEffect, useState } from 'react'
import type { ChangeEvent, FormEvent } from 'react'
import { useNavigate } from 'react-router-dom'

import { getAccessToken } from '../../features/auth'
import { getCurrentUser, updateUser } from '../../services'
import type { User } from '../../models'

import './EditarPerfil.css'

interface PerfilFormState {
  nome: string
  email: string
  role: string
  senha: string
  confirmarSenha: string
}

function validatePasswordChange(senha: string, confirmarSenha: string): string | null {
  const senhaTrimmed = senha.trim()
  const confirmTrimmed = confirmarSenha.trim()

  if (!senhaTrimmed && !confirmTrimmed) {
    return null
  }

  if (!senhaTrimmed || !confirmTrimmed) {
    return 'Preencha os dois campos de senha para alterar sua senha.'
  }

  if (senhaTrimmed.length < 8) {
    return 'A senha deve ter pelo menos 8 caracteres.'
  }

  if (senhaTrimmed !== confirmTrimmed) {
    return 'As senhas nao coincidem.'
  }

  return null
}

const emptyFormState: PerfilFormState = {
  nome: '',
  email: '',
  role: 'aluno',
  senha: '',
  confirmarSenha: '',
}

export default function EditarPerfilPage() {
  const navigate = useNavigate()
  const [user, setUser] = useState<User | null>(null)
  const [formState, setFormState] = useState<PerfilFormState>(emptyFormState)
  const [isLoading, setIsLoading] = useState(true)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [isSaved, setIsSaved] = useState(false)
  const [errorMessage, setErrorMessage] = useState<string | null>(null)

  useEffect(() => {
    async function loadUser() {
      const token = getAccessToken()
      if (!token) {
        setErrorMessage('Sessao nao encontrada. Faca login novamente.')
        setIsLoading(false)
        return
      }

      try {
        const currentUser = await getCurrentUser(token)
        setUser(currentUser)
        setFormState({
          nome: currentUser.nome,
          email: currentUser.email,
          role: currentUser.role,
          senha: '',
          confirmarSenha: '',
        })
      } catch {
        setErrorMessage('Nao foi possivel carregar os dados do usuario.')
      } finally {
        setIsLoading(false)
      }
    }

    void loadUser()
  }, [])

  const handleChange = (
    event: ChangeEvent<HTMLInputElement | HTMLSelectElement>,
  ) => {
    const { name, value } = event.target

    setFormState((currentState) => ({
      ...currentState,
      [name]: value,
    }))

    if (isSaved) {
      setIsSaved(false)
    }

    if (errorMessage) {
      setErrorMessage(null)
    }
  }

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()

    if (!user) {
      return
    }

    const token = getAccessToken()
    if (!token) {
      setErrorMessage('Sessao nao encontrada. Faca login novamente.')
      return
    }

    const passwordError = validatePasswordChange(formState.senha, formState.confirmarSenha)
    if (passwordError) {
      setErrorMessage(passwordError)
      return
    }

    try {
      setIsSubmitting(true)
      setErrorMessage(null)

      await updateUser(
        user.id,
        {
          nome: formState.nome.trim(),
          email: formState.email.trim().toLowerCase(),
          role: formState.role as 'aluno' | 'professor',
          senha: formState.senha.trim() ? formState.senha : undefined,
        },
        token,
      )

      setFormState((currentState) => ({
        ...currentState,
        senha: '',
        confirmarSenha: '',
      }))

      navigate('/app', { replace: true })
    } catch {
      setErrorMessage('Nao foi possivel atualizar o perfil. Tente novamente.')
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <section className="editar-perfil-page" aria-label="Editar perfil do usuario">
      <header className="editar-perfil-header">
        <div>
          <p className="editar-perfil-eyebrow">Conta</p>
          <h1>Editar perfil</h1>
        </div>
      </header>

      <form className="editar-perfil-card" onSubmit={handleSubmit}>
        {isLoading && <p>Carregando dados do perfil...</p>}

        {!isLoading && (
          <>
            {errorMessage && <p className="index-error">{errorMessage}</p>}

            <div className="field-group">
              <label className="field">
                <span>Nome</span>
                <input
                  type="text"
                  name="nome"
                  value={formState.nome}
                  onChange={handleChange}
                  placeholder="Digite seu nome"
                />
              </label>

              <label className="field">
                <span>Email</span>
                <input
                  type="email"
                  name="email"
                  value={formState.email}
                  onChange={handleChange}
                  placeholder="seu@email.com"
                />
              </label>
            </div>

            <div className="field-group field-group--single">
              <label className="field">
                <span>Perfil</span>
                <select name="role" value={formState.role} onChange={handleChange}>
                  <option value="aluno">Aluno</option>
                  <option value="professor">Professor</option>
                </select>
              </label>
            </div>

            <div className="field-group field-group--single">
              <label className="field">
                <span>Senha</span>
                <input
                  type="password"
                  name="senha"
                  value={formState.senha}
                  onChange={handleChange}
                  placeholder="Digite a nova senha"
                />
              </label>
            </div>

            <div className="field-group field-group--single">
              <label className="field">
                <span>Confirmar senha</span>
                <input
                  type="password"
                  name="confirmarSenha"
                  value={formState.confirmarSenha}
                  onChange={handleChange}
                  placeholder="Confirme a nova senha"
                />
              </label>
            </div>

            <div className="editar-perfil-actions">
              <button
                type="button"
                className="secondary-button"
                onClick={() => navigate('/app', { replace: true })}
              >
                Cancelar
              </button>
              <button type="submit" className="primary-button" disabled={isSubmitting}>
                {isSubmitting ? 'Salvando...' : 'Salvar alterações'}
              </button>
            </div>

            {isSaved && <p className="save-success">Perfil atualizado com sucesso.</p>}
          </>
        )}
      </form>
    </section>
  )
}
