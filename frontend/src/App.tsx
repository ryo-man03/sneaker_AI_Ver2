// file: src/App.tsx
import { useEffect, useState } from 'react'
import { Navigate, Route, Routes, useLocation, useNavigate } from 'react-router-dom'
import { Sidebar } from './components/Sidebar'
import { Topbar } from './components/Topbar'
import { AdminPage } from './pages/AdminPage'
import { BuyScorePage } from './pages/BuyScorePage'
import { ClosetPage } from './pages/ClosetPage'
import { DataOpsPage } from './pages/DataOpsPage'
import { DashboardPage } from './pages/DashboardPage'
import { DetailPage } from './pages/DetailPage'
import { LoginPage } from './pages/LoginPage'
import { MarketPage } from './pages/MarketPage'
import { NotificationsPage } from './pages/NotificationsPage'
import { PlaceholderPage } from './pages/PlaceholderPage'
import { PortfolioPage } from './pages/PortfolioPage'
import { SearchPage } from './pages/SearchPage'
import { StocksPage } from './pages/StocksPage'
import { WishlistPage } from './pages/WishlistPage'
import type { AppPage } from './types/navigation'

const placeholderMap: Record<Exclude<AppPage, 'dashboard' | 'search' | 'detail' | 'market' | 'stocks' | 'closet' | 'wishlist' | 'portfolio' | 'notifications' | 'buyscore' | 'admin' | 'dataops'>, string> = {
  profile: 'ユーザー情報 / 嗜好',
}

const appPages: AppPage[] = [
  'dashboard',
  'search',
  'detail',
  'closet',
  'wishlist',
  'portfolio',
  'market',
  'stocks',
  'notifications',
  'profile',
  'buyscore',
  'admin',
  'dataops',
]

function pageFromPathname(pathname: string): AppPage {
  const normalized = pathname.replace(/^\//, '')
  return appPages.includes(normalized as AppPage) ? (normalized as AppPage) : 'dashboard'
}

function App() {
  const navigate = useNavigate()
  const location = useLocation()

  const [isAuthenticated, setIsAuthenticated] = useState(() => {
    return Boolean(localStorage.getItem('sm_access_token'))
  })
  const [focusedSku, setFocusedSku] = useState('555088-001')
  const [searchQuery, setSearchQuery] = useState('')

  const activePage = isAuthenticated ? pageFromPathname(location.pathname) : 'dashboard'

  useEffect(() => {
    if (isAuthenticated && location.pathname === '/login') {
      navigate('/dashboard', { replace: true })
    }
  }, [isAuthenticated, location.pathname, navigate])

  const onLogin = () => {
    setIsAuthenticated(true)
    navigate('/dashboard', { replace: true })
  }

  const onNavigatePage = (page: AppPage) => {
    navigate(`/${page}`)
  }

  const onOpenDetail = (sku: string) => {
    setFocusedSku(sku)
    onNavigatePage('detail')
  }

  const onGlobalSearch = (query: string) => {
    setSearchQuery(query)
    onNavigatePage('search')
  }

  if (!isAuthenticated) {
    return <LoginPage onLogin={onLogin} />
  }

  return (
    <div className="app workspace">
      <Sidebar activePage={activePage} onNavigate={onNavigatePage} />
      <main className="content">
        <Topbar page={activePage} onGlobalSearch={onGlobalSearch} />
        <Routes>
          <Route path="/dashboard" element={<DashboardPage onOpenDetail={onOpenDetail} />} />
          <Route
            path="/search"
            element={
              <SearchPage
                query={searchQuery}
                onQueryChange={setSearchQuery}
                onOpenDetail={onOpenDetail}
              />
            }
          />
          <Route path="/detail" element={<DetailPage sku={focusedSku} />} />
          <Route path="/closet" element={<ClosetPage />} />
          <Route path="/wishlist" element={<WishlistPage />} />
          <Route path="/portfolio" element={<PortfolioPage />} />
          <Route path="/market" element={<MarketPage />} />
          <Route path="/stocks" element={<StocksPage />} />
          <Route path="/notifications" element={<NotificationsPage />} />
          <Route path="/buyscore" element={<BuyScorePage />} />
          <Route path="/admin" element={<AdminPage />} />
          <Route path="/dataops" element={<DataOpsPage />} />
          {Object.entries(placeholderMap).map(([page, subtitle]) => (
            <Route
              key={page}
              path={`/${page}`}
              element={<PlaceholderPage title={page.toUpperCase()} subtitle={subtitle} />}
            />
          ))}
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
          <Route path="/login" element={<Navigate to="/dashboard" replace />} />
          <Route path="*" element={<Navigate to="/dashboard" replace />} />
        </Routes>
      </main>
    </div>
  )
}

export default App
