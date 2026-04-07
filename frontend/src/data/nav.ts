// file: src/data/nav.ts
import type { AppPage, NavSection } from '../types/navigation'

export const NAV_SECTIONS: NavSection[] = [
  {
    label: 'メイン',
    items: [
      { key: 'dashboard', label: 'ダッシュボード', icon: '⬡' },
      { key: 'search', label: 'スニーカー検索', icon: '⌕' },
      { key: 'detail', label: 'スニーカー詳細', icon: '◈' },
    ],
  },
  {
    label: 'アセット管理',
    items: [
      { key: 'closet', label: 'Digital Closet', icon: '▣', badge: '12' },
      { key: 'wishlist', label: 'ウィッシュリスト', icon: '◇', badge: '5' },
      { key: 'portfolio', label: 'ROI / ポートフォリオ', icon: '▲' },
    ],
  },
  {
    label: 'マーケット',
    items: [
      { key: 'market', label: '市場価格 / 相場', icon: '◎' },
      { key: 'stocks', label: '株価監視', icon: '↗' },
      {
        key: 'notifications',
        label: '通知センター',
        icon: '◉',
        badge: '3',
        tone: 'alert',
      },
    ],
  },
  {
    label: '設定 / 管理',
    items: [
      { key: 'profile', label: 'プロフィール', icon: '◻' },
      { key: 'buyscore', label: 'BuyScore 調整', icon: '⬡' },
      { key: 'admin', label: '管理コンソール', icon: '⚙' },
      { key: 'dataops', label: 'データ収集 / AI', icon: '⊞' },
    ],
  },
]

export const PAGE_TITLES: Record<AppPage, string> = {
  dashboard: 'DASHBOARD',
  search: 'SEARCH',
  detail: 'SNEAKER DETAIL',
  closet: 'DIGITAL CLOSET',
  wishlist: 'WISHLIST',
  portfolio: 'PORTFOLIO / ROI',
  market: 'MARKET DATA',
  stocks: 'STOCK MONITOR',
  notifications: 'NOTIFICATIONS',
  profile: 'PROFILE',
  buyscore: 'BUYSCORE TUNING',
  admin: 'ADMIN CONSOLE',
  dataops: 'DATA OPS',
}
