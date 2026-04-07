// file: src/components/Sidebar.tsx
import { NAV_SECTIONS } from '../data/nav'
import type { AppPage } from '../types/navigation'

type SidebarProps = {
  activePage: AppPage
  onNavigate: (page: AppPage) => void
}

export function Sidebar({ activePage, onNavigate }: SidebarProps) {
  return (
    <aside className="sidebar">
      <div className="logo">
        <div className="logo-text">SOLE//MATRIX</div>
        <div className="logo-sub">SNEAKER INTELLIGENCE v3.0</div>
      </div>

      <div className="nav-section">
        {NAV_SECTIONS.map((section) => (
          <div key={section.label}>
            <div className="nav-label">{section.label}</div>
            {section.items.map((item) => (
              <button
                key={item.key}
                className={`nav-item ${activePage === item.key ? 'active' : ''}`}
                type="button"
                onClick={() => onNavigate(item.key)}
              >
                <span className="nav-icon">{item.icon}</span>
                <span>{item.label}</span>
                {item.badge ? (
                  <span className={`nav-badge ${item.tone === 'alert' ? 'alert' : ''}`}>
                    {item.badge}
                  </span>
                ) : null}
              </button>
            ))}
          </div>
        ))}
      </div>

      <div className="sidebar-footer">
        <div className="avatar">YT</div>
        <div>
          <div className="user-name">山田 太郎</div>
          <div className="user-tier">PRO TIER</div>
        </div>
      </div>
    </aside>
  )
}
