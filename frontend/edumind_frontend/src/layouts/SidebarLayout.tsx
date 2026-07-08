import { NavLink, Outlet } from 'react-router-dom'

import './SidebarLayout.css'

export function SidebarLayout() {
  return (
    <div className="sidebar-layout">
      <header className="sidebar-layout__topbar">
        <h1 className="sidebar-layout__brand">Edumind</h1>
        <nav className="sidebar-layout__nav" aria-label="Navegacao principal">
          <NavLink to="/app" end>
            Inicio
          </NavLink>
        </nav>
      </header>
      <main className="sidebar-layout__content">
        <Outlet />
      </main>
    </div>
  )
}
