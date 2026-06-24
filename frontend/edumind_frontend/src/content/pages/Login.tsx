import { useState } from 'react'
import type { ChangeEvent, FormEvent } from 'react'
import './Login.css'

interface LoginFeature {
  title: string
  description: string
}

interface LoginFormState {
  email: string
  password: string
}

const loginFeatures: LoginFeature[] = [
  {
    title: 'Trilhas de estudo personalizadas',
    description: 'Organize o aprendizado com foco no ritmo de cada turma.',
  },
  {
    title: 'Espaço colaborativo entre turmas',
    description: 'Conecte alunos e professores em uma experiência contínua.',
  },
  {
    title: 'Acompanhamento em tempo real',
    description: 'Visualize o progresso e ajuste a condução das aulas.',
  },
]

function LoginPage() {
  const currentYear = new Date().getFullYear()
  const [formState, setFormState] = useState<LoginFormState>({
    email: '',
    password: '',
  })
  const [showPassword, setShowPassword] = useState(false)

  const handleEmailChange = (event: ChangeEvent<HTMLInputElement>) => {
    setFormState((currentState) => ({
      ...currentState,
      email: event.target.value,
    }))
  }

  const handlePasswordChange = (event: ChangeEvent<HTMLInputElement>) => {
    setFormState((currentState) => ({
      ...currentState,
      password: event.target.value,
    }))
  }

  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
  }

  return (
    <main className="login-page">
      <aside className="login-brand-panel" aria-label="Apresentação da marca Edumind">
        <div className="brand-orb" aria-hidden="true" />
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
            <p className="eyebrow">Sala de aula digital</p>
            <h1>Aprender e ensinar, num só lugar.</h1>
            <p>
              Um ambiente claro para professores criarem aulas e alunos acompanharem
              a jornada com foco.
            </p>
          </div>

          <ul className="feature-list">
            {loginFeatures.map((feature) => (
              <li key={feature.title} className="feature-item">
                <span className="feature-icon" aria-hidden="true">
                  <svg viewBox="0 0 24 24" focusable="false" aria-hidden="true">
                    <path d="M10 15.5 6.8 12.3l-1.6 1.6L10 18.7 19 9.7l-1.6-1.6L10 15.5Z" />
                  </svg>
                </span>
                <div>
                  <strong>{feature.title}</strong>
                  <p>{feature.description}</p>
                </div>
              </li>
            ))}
          </ul>
        </div>

        <p className="brand-footer">© {currentYear} Edumind</p>
      </aside>

      <section className="login-form-panel" aria-label="Acesso à conta">
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
          <h2>Bem-vindo de volta</h2>
          <p>Entre na sua conta para acessar a sala de aula.</p>
        </div>

        <div className="login-card">
          <form className="login-form" onSubmit={handleSubmit}>
            <label className="field">
              <span>Email</span>
              <div className="input-shell">
                <span className="input-icon" aria-hidden="true">
                  <svg viewBox="0 0 24 24" focusable="false" aria-hidden="true">
                    <path d="M4 6.5h16a1.5 1.5 0 0 1 1.5 1.5v8A1.5 1.5 0 0 1 20 17.5H4A1.5 1.5 0 0 1 2.5 16V8A1.5 1.5 0 0 1 4 6.5Zm0 2.02V16h16V8.52l-8 4.6-8-4.6Zm.92-1.02L12 11.84l7.08-4.34H4.92Z" />
                  </svg>
                </span>
                <input
                  type="email"
                  name="email"
                  value={formState.email}
                  onChange={handleEmailChange}
                  autoComplete="email"
                  placeholder="voce@gmail.com"
                />
              </div>
            </label>

            <label className="field">
              <div className="field-head">
                <span>Senha</span>
                <a href="/" onClick={(event) => event.preventDefault()}>
                  Esqueceu?
                </a>
              </div>
              <div className="input-shell">
                <span className="input-icon" aria-hidden="true">
                  <svg viewBox="0 0 24 24" focusable="false" aria-hidden="true">
                    <path d="M17 10h-1V8.5a4 4 0 0 0-8 0V10H7a1.5 1.5 0 0 0-1.5 1.5v6A1.5 1.5 0 0 0 7 19h10a1.5 1.5 0 0 0 1.5-1.5v-6A1.5 1.5 0 0 0 17 10Zm-2.75 0h-4.5V8.5a2.25 2.25 0 0 1 4.5 0V10Zm-2.25 3.1a1.4 1.4 0 1 1 0 2.8 1.4 1.4 0 0 1 0-2.8Z" />
                  </svg>
                </span>
                <input
                  type={showPassword ? 'text' : 'password'}
                  name="password"
                  value={formState.password}
                  onChange={handlePasswordChange}
                  autoComplete="current-password"
                  placeholder="••••••••"
                />
                <button
                  type="button"
                  className="password-toggle"
                  onClick={() => setShowPassword((currentValue) => !currentValue)}
                  aria-label={showPassword ? 'Ocultar senha' : 'Mostrar senha'}
                >
                  <svg viewBox="0 0 24 24" focusable="false" aria-hidden="true">
                    {showPassword ? (
                      <path d="M4.2 4.9 3 6.1l2.3 2.3C3.6 9.7 2.1 11.7 1.5 12c1.7 3.5 5.5 7.5 10.5 7.5 1.6 0 3.1-.3 4.4-.9l3 3 1.2-1.2-16.4-16.5Zm4.1 4.1 1.7 1.7a2.8 2.8 0 0 0-.1.8 2.9 2.9 0 0 0 2.9 2.9c.3 0 .6 0 .8-.1l1.7 1.7c-.8.4-1.7.7-2.7.7a5 5 0 0 1-4.9-5c0-1 .3-1.9.6-2.7Zm8.7 2c.1.2.3.4.4.6-1.6 2.8-4.5 4.7-8 4.7l-1-.1 1.7 1.7h.1c4 0 7.7-2.3 9.8-5.8-.8-1.4-1.8-2.6-3-3.7l-1.5 1.5c.5.3.9.7 1.5 1.1Z" />
                    ) : (
                      <>
                        <path d="M12 5c-5 0-8.8 4-10.5 7 1.7 3 5.5 7 10.5 7s8.8-4 10.5-7C20.8 9 17 5 12 5Zm0 11.5A4.5 4.5 0 1 1 12 7a4.5 4.5 0 0 1 0 9.5Zm0-2A2.5 2.5 0 1 0 12 9a2.5 2.5 0 0 0 0 5.5Z" />
                      </>
                    )}
                  </svg>
                </button>
              </div>
            </label>

            <button type="submit" className="submit-button">
              Entrar
            </button>
          </form>

          <p className="signup-text">
            Novo na Edumind?{' '}
            <a href="/" onClick={(event) => event.preventDefault()}>
              Criar conta
            </a>
          </p>
        </div>

        <p className="policy-text">
          Ao continuar você aceita os termos de uso e a política de privacidade.
        </p>
      </section>
    </main>
  )
}

export { LoginPage }