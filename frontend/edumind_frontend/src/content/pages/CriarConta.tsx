import { useState } from 'react'
import type { ChangeEvent, FormEvent } from 'react'
import { Link, useNavigate } from 'react-router-dom'

import { setAuthSession } from '../../features/auth'
import type { CreateUserRequest, UserRole } from '../../models/User'
import { createUser } from '../../services'
import { getAuthTokens } from '../../utils/authUtils'
import { ApiRequestError } from '../../utils/requests'

import './CriarConta.css'

interface CreateAccountFormState {
  nome: string
  email: string
  senha: string
  role: UserRole | ''
}

const initialFormState: CreateAccountFormState = {
  nome: '',
  email: '',
  senha: '',
  role: '',
}

function getErrorMessage(details: unknown): string | null {
  if (!details || typeof details !== 'object') {
    return null
  }

  const detailEntries = Object.entries(details as Record<string, unknown>)

  for (const [, value] of detailEntries) {
    if (Array.isArray(value)) {
      const firstStringMessage = value.find((item) => typeof item === 'string')
      if (typeof firstStringMessage === 'string') {
        return firstStringMessage
      }
    }

    if (typeof value === 'string') {
      return value
    }
  }

  return null
}

function CreateAccountPage() {
  const navigate = useNavigate()
  const [formState, setFormState] = useState<CreateAccountFormState>(initialFormState)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [feedbackMessage, setFeedbackMessage] = useState<string | null>(null)
  const [isSuccess, setIsSuccess] = useState(false)

  const handleChange = (event: ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    if (feedbackMessage) {
      setFeedbackMessage(null)
      setIsSuccess(false)
    }

    const { name, value } = event.target
    setFormState((currentState) => ({
      ...currentState,
      [name]: value,
    }))
  }

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()

    if (isSubmitting) {
      return
    }

    setIsSubmitting(true)
    setFeedbackMessage(null)
    setIsSuccess(false)

    try {
      const payload: CreateUserRequest = {
        nome: formState.nome.trim(),
        email: formState.email.trim().toLowerCase(),
        senha: formState.senha,
        role: formState.role as UserRole,
      }

      await createUser(payload)

      const tokens = await getAuthTokens({
        email: payload.email,
        password: payload.senha,
      })

      setAuthSession(tokens)
      navigate('/app', { replace: true })
      setFormState(initialFormState)
    } catch (error) {
      if (error instanceof ApiRequestError) {
        const message = getErrorMessage(error.details) ?? error.message
        setFeedbackMessage(message || 'Não foi possível criar a conta. Tente novamente.')
      } else {
        setFeedbackMessage('Não foi possível criar a conta. Tente novamente.')
      }

      setIsSuccess(false)
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <main className="login-page create-account-page">
      <aside className="login-brand-panel" aria-label="Apresentação da marca Edumind">
        <div className="brand-content">
          <div className="brand-badge">
            <span className="brand-badge-icon" aria-hidden="true">
              <svg viewBox="0 0 24 24" focusable="false" aria-hidden="true">
                <path d="M12 3 2.5 8.5 12 14l7.75-4.5V15h1.75V8.5L12 3Z" />
                <path d="M7.25 13.2V16c0 1.5 2.16 2.75 4.75 2.75S16.75 17.5 16.75 16v-2.8L12 16l-4.75-2.8Z" />
              </svg>
            </span>
            Edumind
          </div>

          <div className="brand-copy">
            <p className="eyebrow">Novo cadastro</p>
            <h1>Crie sua conta e comece sua jornada.</h1>
            <p>
              Organize turmas, acompanhe o aprendizado e conecte professores e alunos em um só ambiente.
            </p>
          </div>
        </div>
      </aside>

      <section className="login-form-panel create-account-form-panel" aria-label="Criar conta">
        <div className="mobile-brand">
          <div className="brand-badge">
            <span className="brand-badge-icon" aria-hidden="true">
              <svg viewBox="0 0 24 24" focusable="false" aria-hidden="true">
                <path d="M12 3 2.5 8.5 12 14l7.75-4.5V15h1.75V8.5L12 3Z" />
                <path d="M7.25 13.2V16c0 1.5 2.16 2.75 4.75 2.75S16.75 17.5 16.75 16v-2.8L12 16l-4.75-2.8Z" />
              </svg>
            </span>
            Edumind
          </div>
        </div>

        <div className="login-copy">
          <h2>Criar conta</h2>
          <p>Preencha os campos abaixo para entrar na plataforma.</p>
        </div>

        <div className="login-card create-account-card">
          <form className="login-form" onSubmit={handleSubmit}>
            <label className="field">
              <span>Nome</span>
              <div className="input-shell">
                <input
                  type="text"
                  name="nome"
                  value={formState.nome}
                  onChange={handleChange}
                  placeholder="Digite seu nome completo"
                />
              </div>
            </label>

            <label className="field">
              <span>Email</span>
              <div className="input-shell">
                <input
                  type="email"
                  name="email"
                  value={formState.email}
                  onChange={handleChange}
                  placeholder="seu@email.com"
                />
              </div>
            </label>

            <label className="field">
              <span>Senha</span>
              <div className="input-shell">
                <input
                  type="password"
                  name="senha"
                  value={formState.senha}
                  onChange={handleChange}
                  placeholder="••••••••"
                />
              </div>
            </label>

            <label className="field">
              <span>Tipo de Conta</span>
              <div className="input-shell">
                <select name="role" value={formState.role} onChange={handleChange}>
                  <option value="" disabled>
                    Selecione um tipo
                  </option>
                  <option value="aluno">Aluno</option>
                  <option value="professor">Professor</option>
                </select>
              </div>
            </label>

            {feedbackMessage && (
              <p className={`form-feedback-message ${isSuccess ? 'form-feedback-message--success' : 'form-feedback-message--error'}`}>
                {feedbackMessage}
              </p>
            )}

            <p className="account-helper-text">
              Os campos acima são os obrigatórios para esta primeira versão da tela.
            </p>

            <button type="submit" className="submit-button" disabled={isSubmitting}>
              {isSubmitting ? 'Cadastrando...' : 'Cadastrar'}
            </button>
          </form>
        </div>

        <p className="signup-text">
          Já possui conta? <Link to="/login">Entrar</Link>
        </p>
      </section>
    </main>
  )
}

export default CreateAccountPage
