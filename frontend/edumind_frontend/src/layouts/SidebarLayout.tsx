import { Outlet } from 'react-router-dom'

import './SidebarLayout.css'

export function SidebarLayout() {
  return (
    <div className="sidebar-layout">
      <main className="sidebar-layout__content">
        <Outlet />
      </main>
    </div>
  )
}
