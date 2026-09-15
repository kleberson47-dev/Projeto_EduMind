import { useNavigate } from 'react-router-dom'

import './ProfessorSidebar.css'

interface ProfessorNavItem {
  label: string
  icon: string
  path?: string
}

interface ProfessorSidebarProps {
  activeItem: 'inicio' | 'turmas'
}

const navItems: ProfessorNavItem[] = [
  { label: 'Início', icon: '▣', path: '/app/inicio_professor' },
  { label: 'Turmas', icon: '◫', path: '/app/turmas-professor' },
  { label: 'Agenda', icon: '◫' },
  { label: 'Atividades', icon: '≋' },
  { label: 'Configurações', icon: '⚙' },
]

export function ProfessorSidebar({ activeItem }: ProfessorSidebarProps) {
  const navigate = useNavigate()

  const createNavigationHandler = (path: string | undefined) => {
    if (path === undefined) {
      return undefined
    }

    return () => navigate(path)
  }

  return (
    <aside className="professor-sidebar">
      <div className="professor-sidebar-brand" aria-label="Logo Edumind">
        <div className="professor-brand-mark">Ed</div>
        <div>
          <div className="professor-brand-title">Edumind</div>
          <div className="professor-brand-subtitle">Área do professor</div>
        </div>
      </div>

      <nav className="professor-sidebar-nav" aria-label="Menu lateral">
        {navItems.map((item) => {
          const isActive = activeItem === 'inicio'
            ? item.label === 'Início'
            : item.label === 'Turmas'

          return (
            <button
              key={item.label}
              type="button"
              className={isActive ? 'professor-nav-item active' : 'professor-nav-item'}
              onClick={createNavigationHandler(item.path)}
            >
              <span className="professor-nav-icon">{item.icon}</span>
              <span>{item.label}</span>
            </button>
          )
        })}
      </nav>

      <div className="professor-assistant-card">
        <div className="professor-assistant-title">Assistente de Ensino IA</div>
        <div className="professor-assistant-copy">Planeje aulas, crie atividades e apoie suas turmas.</div>
      </div>
    </aside>
  )
}