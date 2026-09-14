import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'

import { clearAuthSession, getAccessToken } from '../../features/auth'
import type { User } from '../../models'
import { getCurrentUser } from '../../services'

import './IndexProfessorPage.css'

interface NavItem {
  label: string
  active?: boolean
  icon: string
}

interface Stat {
  label: string
  value: string
  detail: string
  icon: string
}

interface Deadline {
  title: string
  course: string
  deadline: string
}

interface Event {
  time: string
  title: string
  course: string
}

interface CourseMetric {
  subject: string
  score: string
  value: number
}

const navItems: NavItem[] = [
  { label: 'Inicio', active: true, icon: '▣' },
  { label: 'Turmas', icon: '◫' },
  { label: 'Agenda', icon: '◫' },
  { label: 'Atividades', icon: '≋' },
  { label: 'Configurações', icon: '⚙' },
]

const stats: Stat[] = [
  { label: 'Turmas ativas', value: '4', detail: 'neste semestre', icon: '▣' },
  { label: 'Total de alunos', value: '126', detail: 'em todas as turmas', icon: '☰' },
  { label: 'Atividades pendentes', value: '7', detail: 'aguardando correção', icon: '✓' },
  { label: 'Média das turmas', value: '8,2', detail: '+0,3 vs. bimestre anterior', icon: '↗' },
]

const deadlines: Deadline[] = [
  { title: 'Corrigir: Modelagem ER', course: 'Banco de Dados', deadline: 'Hoje, 23:59' },
  { title: 'Publicar: Quiz de Nuvem', course: 'Computação em Nuvem', deadline: 'Amanhã, 18:00' },
  { title: 'Revisar: Projetos responsivos', course: 'Programação Web', deadline: 'Sex, 20 · 22:00' },
  { title: 'Preparar: Lista de exercícios', course: 'Inteligência Artificial', deadline: 'Seg, 23 · 12:00' },
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

const events: Event[] = [
  { time: '09:00', title: 'Aula ao vivo: Consultas SQL', course: 'Banco de Dados' },
  { time: '14:30', title: 'Monitoria de IA', course: 'Inteligência Artificial' },
  { time: '19:00', title: 'Reunião de planejamento', course: 'Programação Web' },
]

const courseMetrics: CourseMetric[] = [
  { subject: 'Computação em Nuvem', score: 'Média 8,5 · 32 alunos', value: 85 },
  { subject: 'Banco de Dados', score: 'Média 8,1 · 38 alunos', value: 81 },
  { subject: 'Programação Web', score: 'Média 7,9 · 29 alunos', value: 79 },
  { subject: 'Inteligência Artificial', score: 'Média 8,3 · 27 alunos', value: 83 },
]

function getUserInitials(name: string): string {
  return name
    .split(' ')
    .filter(Boolean)
    .slice(0, 2)
    .map((part) => part[0]?.toUpperCase() ?? '')
    .join('') || 'US'
}

export default function IndexProfessorPage() {
  const navigate = useNavigate()
  const [menuOpen, setMenuOpen] = useState(false)
  const [user, setUser] = useState<User | null>(null)

  useEffect(() => {
    async function loadCurrentUser() {
      const token = getAccessToken()
      if (!token) return

      try {
        const profile = await getCurrentUser(token)
        setUser(profile)

        if (profile.role !== 'professor') {
          navigate('/app/inicio_aluno', { replace: true })
        }
      } catch {
        // A página continua disponível mesmo que os dados do perfil não carreguem.
      }
    }

    void loadCurrentUser()
  }, [navigate])

  const handleLogout = () => {
    clearAuthSession()
    navigate('/login', { replace: true })
  }

  const handleOpenConfig = () => {
    navigate('/app/editar-perfil')
  }

  if (user && user.role !== 'professor') return null

  const displayName = user?.nome ?? 'Professor'
  const firstName = displayName.split(' ')[0] ?? 'Professor'
  const profileInitials = getUserInitials(displayName)

  return (
    <div className="dashboard-aluno-page dashboard-professor-page">
      <aside className="dashboard-aluno-sidebar">
        <div className="sidebar-brand" aria-label="Logo Edumind">
          <div className="brand-mark">🔎</div>
          <div>
            <div className="brand-title">Edumind</div>
            <div className="brand-subtitle">Área do professor</div>
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
          <div className="assistant-title">Assistente de Ensino IA</div>
          <div className="assistant-copy">Planeje aulas, crie atividades e apoie suas turmas.</div>
        </div>
      </aside>

      <main className="dashboard-aluno-main">
        <header className="dashboard-header">
          <div className="search-box" aria-label="Buscar turmas e atividades">
            <span className="search-icon">⌕</span>
            <span>Buscar turmas, alunos, atividades...</span>
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
              onClick={() => setMenuOpen((currentValue) => !currentValue)}
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
                <div className="profile-menu-role">Professor</div>
              </div>

              <button type="button" className="profile-menu-item" onClick={handleOpenConfig}>
                <span className="profile-menu-icon">⚙</span>
                <span>Configurações</span>
              </button>

              <button type="button" className="profile-menu-item danger" onClick={handleLogout}>
                <span className="profile-menu-icon">↩</span>
                <span>Sair</span>
              </button>
            </div>
          )}

          <div className="welcome-banner">
            <div className="banner-date">Terça-feira, 19 de agosto</div>
            <h1>Olá, professor {firstName}</h1>
            <p>Você tem 7 atividades aguardando correção e 3 compromissos nos próximos dias.</p>
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
              <div className="panel-title">Pendências recentes</div>
              <button type="button" className="mini-link">Ver todas ↗</button>
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
              <div className="panel-title">Próximos 7 dias</div>
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

        <section className="performance-panel panel" aria-label="Desempenho das turmas">
          <h2 className="performance-title">Desempenho das turmas</h2>

          <div className="performance-grid">
            {courseMetrics.map((course) => (
              <div key={course.subject} className="performance-item">
                <div className="performance-head">
                  <span className="performance-name">{course.subject}</span>
                  <span className="performance-score">{course.score}</span>
                </div>
                <div className="performance-track" aria-label={`${course.subject} com média de ${course.value}%`}>
                  <span className="performance-fill" style={{ width: `${course.value}%` }} />
                </div>
              </div>
            ))}
          </div>
        </section>
      </main>
    </div>
  )
}