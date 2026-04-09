// file: src/components/Topbar.tsx
import { useState } from 'react'
import { PAGE_TITLES } from '../data/nav'
import type { AppPage } from '../types/navigation'

type TopbarProps = {
  page: AppPage
  onGlobalSearch: (query: string) => void
}

export function Topbar({ page, onGlobalSearch }: TopbarProps) {
  const [query, setQuery] = useState('')

  const submitSearch = () => {
    onGlobalSearch(query.trim())
  }

  return (
    <header className="topbar">
      <div className="topbar-title">
        SOLE//MATRIX / <span>{PAGE_TITLES[page]}</span>
      </div>
      <div className="search-box">
        <span>⌕</span>
        <input
          placeholder="SKU、ブランド、モデルで検索..."
          value={query}
          onChange={(event) => setQuery(event.target.value)}
          onKeyDown={(event) => {
            if (event.key === 'Enter') {
              submitSearch()
            }
          }}
        />
      </div>
      <button className="topbar-btn" type="button" aria-label="検索実行" onClick={submitSearch}>
        ➤
      </button>
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
