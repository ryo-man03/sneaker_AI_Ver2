// file: src/components/Topbar.tsx
import { PAGE_TITLES } from '../data/nav'
import type { AppPage } from '../types/navigation'

type TopbarProps = {
  page: AppPage
}

export function Topbar({ page }: TopbarProps) {
  return (
    <header className="topbar">
      <div className="topbar-title">
        SOLE//MATRIX / <span>{PAGE_TITLES[page]}</span>
      </div>
      <div className="search-box">
        <span>⌕</span>
        <input placeholder="SKU、ブランド、モデルで検索..." />
      </div>
      <button className="topbar-btn" type="button" aria-label="通知">
        🔔
      </button>
      <button className="topbar-btn" type="button" aria-label="設定">
        ⚙
      </button>
      <button className="topbar-btn" type="button" aria-label="拡張">
        🔌
      </button>
    </header>
  )
}
