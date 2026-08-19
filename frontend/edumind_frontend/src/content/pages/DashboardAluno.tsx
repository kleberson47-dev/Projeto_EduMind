import { useEffect, useState } from 'react'

import type { User } from '../../models'
import { getCurrentUser } from '../../services'
import { getAccessToken } from '../../features/auth'

import './DashboardAluno.css'

type NavItem = {
  label: string
  active?: boolean
  icon: string
}

type Stat = {
  label: string
  value: string
  detail: string
  icon: string
}

type Deadline = {
  title: string
  course: string
  deadline: string
}

const navItems: NavItem[] = [
  { label: 'Inicio', active: true, icon: '▣' },
  { label: 'Turmas', icon: '◫' },
  { label: 'Agenda', icon: '◫' },
  { label: 'Atividades', icon: '≋' },
  { label: 'Configurações', icon: '⚙' },
]

const stats: Stat[] = [
  { label: 'Turmas matriculadas', value: '4', detail: 'neste semestre', icon: '▣' },
  { label: 'Atividades pendentes', value: '7', detail: '3 entregam esta semana', icon: '☰' },
  { label: 'Atividades concluídas', value: '23', detail: 'de 30 no total', icon: '✓' },
  { label: 'Média geral', value: '8,6', detail: '+0,4 vs. bimestre anterior', icon: '↗' },
]

const deadlines: Deadline[] = [
  { title: 'Trabalho: Modelagem ER', course: 'Banco de Dados', deadline: 'Hoje, 23:59' },
  { title: 'Quiz: Camadas de Nuvem', course: 'Computação em Nuvem', deadline: 'Amanhã, 18:00' },
  { title: 'Projeto: Landing responsiva', course: 'Programação Web', deadline: 'Sex, 20 · 22:00' },
  { title: 'Lista 4: Redes Neurais', course: 'Inteligência Artificial', deadline: 'Seg, 23 · 12:00' },
]

const weekDays = [
  { day: 'QUA', date: 13 },
  { day: 'QUI', date: 14 },
  { day: 'SEX', date: 15 },
  { day: 'SÁB', date: 16 },
  { day: 'DOM', date: 17 },
  { day: 'SEG', date: 18 },
  { day: 'TER', date: 19 },
]

const events = [
  { time: '09:00', title: 'Aula ao vivo: Consultas SQL', course: 'Banco de Dados' },
  { time: '14:30', title: 'Monitoria de IA', course: 'Inteligência Artificial' },
  { time: '19:00', title: 'Entrega do protótipo', course: 'Programação Web' },
]

const performanceMetrics = [
  {
    left: { subject: 'Computação em Nuvem', score: 'Nota 9.1 · 82%', value: 82 },
    right: { subject: 'Banco de Dados', score: 'Nota 8.4 · 68%', value: 68 },
  },
  {
    left: { subject: 'Programação Web', score: 'Nota 8.9 · 74%', value: 74 },
    right: { subject: 'Inteligência Artificial', score: 'Nota 7.9 · 55%', value: 55 },
  },
]

function getUserInitials(name: string): string {
  return name
    .split(' ')
    .filter(Boolean)
    .slice(0, 2)
    .map((part) => part[0]?.toUpperCase() ?? '')
    .join('') || 'US'
}

function formatRole(role: User['role']): string {
  if (role === 'aluno') return 'Aluno'
  if (role === 'professor') return 'Professor'
  return 'Usuário'
}

export default function DashboardAlunoPage() {
  const [menuOpen, setMenuOpen] = useState(false)
  const [user, setUser] = useState<User | null>(null)

  useEffect(() => {
    async function loadCurrentUser() {
      const token = getAccessToken()
      if (!token) {
        return
      }

      try {
        const profile = await getCurrentUser(token)
        setUser(profile)
      } catch {
        // ignorado intencionalmente: a página continua mesmo sem dados do usuário
      }
    }

    void loadCurrentUser()
  }, [])

  const displayName = user?.nome ?? 'Usuário'
  const firstName = displayName.split(' ')[0] ?? 'Usuário'
  const profileInitials = getUserInitials(displayName)
  const profileRole = user ? formatRole(user.role) : 'Aluno'

  return (
    <div className="dashboard-aluno-page">
      <aside className="dashboard-aluno-sidebar">
        <div className="sidebar-brand" aria-label="Logo Edumind">
          <div className="brand-mark">🔎</div>
          <div>
            <div className="brand-title">Edumind</div>
            <div className="brand-subtitle">Área do aluno</div>
          </div>
        </div>

        <nav className="sidebar-nav" aria-label="Menu lateral">
          {navItems.map((item) => (
            <button key={item.label} type="button" className={item.active ? 'nav-item active' : 'nav-item'}>
              <span className="nav-icon">{item.icon}</span>
              <span>{item.label}</span>
            </button>
          ))}
        </nav>

        <div className="assistant-card">
          <div className="assistant-title">Assistente de Estudos IA</div>
          <div className="assistant-copy">Tire dúvidas sobre suas disciplinas a qualquer momento.</div>
        </div>
      </aside>

      <main className="dashboard-aluno-main">
        <header className="dashboard-header">
          <div className="search-box" aria-label="Buscar turmas e atividades">
            <span className="search-icon">⌕</span>
            <span>Buscar turmas, atividades...</span>
          </div>

          <div className="header-actions">
            <button type="button" className="icon-button" aria-label="Notificações">
              <span className="bell-icon">🔔</span>
            </button>

            <button
              type="button"
              className="profile-chip"
              aria-label="Perfil do usuário"
              aria-expanded={menuOpen}
              onClick={() => setMenuOpen((prev) => !prev)}
            >
              <div className="profile-badge">{profileInitials}</div>
              <span>{firstName}</span>
            </button>
          </div>
        </header>

        <section className="dashboard-surface">
          {menuOpen && user && (
            <div className="profile-menu" aria-label="Menu do perfil">
              <div className="profile-menu-head">
                <div className="profile-menu-name">{user.nome}</div>
                <div className="profile-menu-role">{profileRole}</div>
              </div>

              <div className="profile-menu-item">
                <span className="profile-menu-icon">⚙</span>
                <span>Configurações</span>
              </div>

              <div className="profile-menu-item danger">
                <span className="profile-menu-icon">↩</span>
                <span>Sair</span>
              </div>
            </div>
          )}

          <div className="welcome-banner">
            <div className="banner-date">Terça-feira, 19 de agosto</div>
            <h1>
              Olá, {displayName} <span className="wave">👋</span>
            </h1>
            <p>Você tem 3 entregas nos próximos dias e sua média subiu para 8,6. Continue assim.</p>
          </div>
        </section>

        <section className="dashboard-stats" aria-label="Estatísticas gerais">
          {stats.map((stat) => (
            <article key={stat.label} className="stat-card">
              <div className="stat-icon">{stat.icon}</div>
              <div className="stat-copy">
                <div className="stat-label">{stat.label}</div>
                <div className="stat-value">{stat.value}</div>
                <div className="stat-detail">{stat.detail}</div>
              </div>
            </article>
          ))}
        </section>

        <section className="dashboard-lower">
          <div className="panel deadlines-panel">
            <div className="panel-header">
              <div className="panel-title">Próximos prazos</div>
              <button type="button" className="mini-link">
                Ver todos ↗
              </button>
            </div>

            <div className="deadline-list">
              {deadlines.map((item) => (
                <div key={item.title} className="deadline-card">
                  <div className="deadline-main">
                    <div className="deadline-title">{item.title}</div>
                    <div className="deadline-course">{item.course}</div>
                  </div>
                  <div className="deadline-badge">{item.deadline}</div>
                </div>
              ))}
            </div>
          </div>

          <div className="panel events-panel">
            <div className="panel-header compact-header">
              <div className="panel-title">Últimos 7 dias</div>
            </div>

            <div className="day-grid" aria-label="Calendário semanal">
              {weekDays.map((item) => (
                <div key={item.day} className={item.date === 19 ? 'day-pill active' : 'day-pill'}>
                  <span>{item.day}</span>
                  <strong>{item.date}</strong>
                </div>
              ))}
            </div>

            <div className="event-list">
              {events.map((event) => (
                <div key={event.title} className="event-item">
                  <div className="event-time">{event.time}</div>
                  <div className="event-copy">
                    <div className="event-title">{event.title}</div>
                    <div className="event-course">{event.course}</div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </section>

        <section className="performance-panel panel" aria-label="Estatísticas de desempenho">
          <h2 className="performance-title">Estatísticas de desempenho</h2>

          <div className="performance-grid">
            {performanceMetrics.map((pair) => (
              <>
                <div key={`${pair.left.subject}-left`} className="performance-item">
                  <div className="performance-head">
                    <span className="performance-name">{pair.left.subject}</span>
                    <span className="performance-score">{pair.left.score}</span>
                  </div>
                  <div className="performance-track" aria-label={`${pair.left.subject} em ${pair.left.value}%`}>
                    <span className="performance-fill" style={{ width: `${pair.left.value}%` }} />
                  </div>
                </div>

                <div key={`${pair.right.subject}-right`} className="performance-item">
                  <div className="performance-head">
                    <span className="performance-name">{pair.right.subject}</span>
                    <span className="performance-score">{pair.right.score}</span>
                  </div>
                  <div className="performance-track" aria-label={`${pair.right.subject} em ${pair.right.value}%`}>
                    <span className="performance-fill" style={{ width: `${pair.right.value}%` }} />
                  </div>
                </div>
              </>
            ))}
          </div>
        </section>
      </main>
    </div>
  )
}
