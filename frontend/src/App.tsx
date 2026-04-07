// file: src/App.tsx
import { useState } from 'react'
import { Sidebar } from './components/Sidebar'
import { Topbar } from './components/Topbar'
import { DashboardPage } from './pages/DashboardPage'
import { DetailPage } from './pages/DetailPage'
import { LoginPage } from './pages/LoginPage'
import { PlaceholderPage } from './pages/PlaceholderPage'
import { SearchPage } from './pages/SearchPage'
import type { AppPage } from './types/navigation'

const placeholderMap: Record<Exclude<AppPage, 'dashboard' | 'search' | 'detail'>, string> = {
  closet: '保有スニーカー管理',
  wishlist: '価格追跡 + アラート設定',
  portfolio: '資産価値 + 投資分析',
  market: 'Ask / Bid / 流動性データ',
  stocks: 'スニーカー関連企業 / 相関分析',
  notifications: 'Price Alert / Release / Trend',
  profile: 'ユーザー情報 / 嗜好',
  buyscore: 'Preference Engine / 重み付け',
  admin: 'システム監視 / 運用管理',
  dataops: 'クローラー / AI / DQM',
}

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [activePage, setActivePage] = useState<AppPage>('dashboard')

  if (!isAuthenticated) {
    return (
      <div className="app">
        <LoginPage onLogin={() => setIsAuthenticated(true)} />
      </div>
    )
  }

  return (
    <div className="app workspace">
      <Sidebar activePage={activePage} onNavigate={setActivePage} />
      <main className="content">
        <Topbar page={activePage} />
        {activePage === 'dashboard' ? <DashboardPage /> : null}
        {activePage === 'search' ? <SearchPage onOpenDetail={() => setActivePage('detail')} /> : null}
        {activePage === 'detail' ? <DetailPage /> : null}
        {activePage !== 'dashboard' && activePage !== 'search' && activePage !== 'detail' ? (
          <PlaceholderPage title={activePage.toUpperCase()} subtitle={placeholderMap[activePage]} />
        ) : null}
      </main>
    </div>
  )
}

export default App
