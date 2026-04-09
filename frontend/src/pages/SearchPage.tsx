// file: src/pages/SearchPage.tsx
import { useEffect, useMemo, useState } from 'react'
import { SNEAKERS, formatYen } from '../data/sneakers'
import { apiFetch } from '../services/api'

type SearchPageProps = {
  query: string
  onQueryChange: (value: string) => void
  onOpenDetail: (sku: string) => void
}

type SearchApiItem = {
  sku: string
  model: string
  brand: string
  retail_price: number
  market_price: number
  buy_score: number
  liquidity: string
  note: string
  rank: number
}

type SearchApiResponse = {
  items: SearchApiItem[]
}

type GroundingCitation = {
  title: string
  url: string
  snippet: string
}

type SearchGroundingResponse = {
  data: {
    query: string
    answer: string
    citations: GroundingCitation[]
  }
  source: string
  updated_at: string
  ai_available: boolean
  partial: boolean
  error_message?: string
}

export function SearchPage({ query, onQueryChange, onOpenDetail }: SearchPageProps) {
  const [apiItems, setApiItems] = useState<SearchApiItem[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [grounding, setGrounding] = useState<SearchGroundingResponse | null>(null)
  const [groundingLoading, setGroundingLoading] = useState(false)
  const [groundingError, setGroundingError] = useState('')

  const normalized = query.trim().toLowerCase()

  useEffect(() => {
    const controller = new AbortController()

    const run = async () => {
      setLoading(true)
      setError('')
      try {
        const params = new URLSearchParams()
        if (query.trim()) {
          params.set('q', query.trim())
        }
        const response = await fetch(`http://127.0.0.1:8000/api/v1/search?${params.toString()}`, {
          signal: controller.signal,
        })

        if (!response.ok) {
          throw new Error('search failed')
        }

        const payload = (await response.json()) as SearchApiResponse
        setApiItems(payload.items)
      } catch {
        setError('検索APIに接続できなかったため、ローカルデータを表示しています。')
        setApiItems([])
      } finally {
        setLoading(false)
      }
    }

    run()
    return () => controller.abort()
  }, [query])

  const filtered = useMemo(() => {
    if (apiItems.length > 0) {
      return apiItems.map((item) => ({
        model: item.model,
        brand: item.brand,
        sku: item.sku,
        marketPrice: item.market_price,
        retailPrice: item.retail_price,
        buyScore: item.buy_score,
        liquidity: (item.liquidity as '高' | '中' | '低') ?? '中',
        note: item.note,
      }))
    }

    if (!normalized) {
      return SNEAKERS
    }
    return SNEAKERS.filter((shoe) => {
      const target = `${shoe.model} ${shoe.brand} ${shoe.sku}`.toLowerCase()
      return target.includes(normalized)
    })
  }, [apiItems, normalized])

  const runGroundedAnswer = async () => {
    setGroundingLoading(true)
    setGroundingError('')
    try {
      const payload = await apiFetch<SearchGroundingResponse>('/search-grounding/answer', {
        method: 'POST',
        body: JSON.stringify({
          query: query.trim() || 'sneaker market trend',
          max_citations: 5,
        }),
      })
      setGrounding(payload)
    } catch {
      setGrounding(null)
      setGroundingError('検索補助AIの取得に失敗しました。fallbackを利用してください。')
    } finally {
      setGroundingLoading(false)
    }
  }

  return (
    <section className="page">
      <div className="section-header">
        <h2>スニーカー検索</h2>
        <span>42サイト統合インデックス</span>
      </div>
      <div className="search-toolbar">
        <div className="search-box wide">
          <span>⌕</span>
          <input
            placeholder="ブランド、モデル名、SKU番号..."
            value={query}
            onChange={(event) => onQueryChange(event.target.value)}
          />
        </div>
        <select className="filter-select" defaultValue="all">
          <option value="all">すべてのブランド</option>
          <option value="NIKE">Nike</option>
          <option value="ADIDAS">Adidas</option>
          <option value="NEW BALANCE">New Balance</option>
          <option value="ASICS">Asics</option>
        </select>
        <select className="filter-select" defaultValue="score">
          <option value="score">並び替え: BuyScore</option>
          <option value="cheap">価格: 安い順</option>
          <option value="expensive">価格: 高い順</option>
        </select>
        <button className="btn-ghost" type="button" onClick={() => void runGroundedAnswer()}>
          検索補助AI回答
        </button>
      </div>
      <div className="panel">
        <h3>検索補助AI回答</h3>
        {groundingLoading ? <p>回答生成中...</p> : null}
        {groundingError ? <p className="form-error">{groundingError}</p> : null}
        {!groundingLoading && !groundingError && !grounding ? <p>未実行</p> : null}
        {grounding ? (
          <>
            <p>{grounding.data.answer}</p>
            <p className="mono">
              source: {grounding.source} / partial: {String(grounding.partial)} / ai_available:{' '}
              {String(grounding.ai_available)}
            </p>
            {grounding.error_message ? <p className="form-error">{grounding.error_message}</p> : null}
            {grounding.data.citations.length === 0 ? <p>citationなし</p> : null}
            <ul>
              {grounding.data.citations.map((citation) => (
                <li key={`${citation.title}-${citation.url}`}>
                  {citation.url ? (
                    <a href={citation.url} target="_blank" rel="noreferrer">
                      {citation.title}
                    </a>
                  ) : (
                    citation.title
                  )}
                  : {citation.snippet}
                </li>
              ))}
            </ul>
          </>
        ) : null}
      </div>
      <div className="panel">
        <h3>検索結果 — {filtered.length}件</h3>
        {loading ? <p>検索中...</p> : null}
        {error ? <p>{error}</p> : null}
        <table className="data-table">
          <thead>
            <tr>
              <th>モデル名</th>
              <th>ブランド</th>
              <th>SKU</th>
              <th>市場価格</th>
              <th>定価</th>
              <th>BuyScore</th>
              <th>流動性</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            {filtered.map((shoe) => (
              <tr key={shoe.sku}>
                <td>
                  <div className="cell-title">{shoe.model}</div>
                  <div className="cell-note">{shoe.note}</div>
                </td>
                <td className="mono cyan">{shoe.brand}</td>
                <td className="mono">{shoe.sku}</td>
                <td className="mono cyan">{formatYen(shoe.marketPrice)}</td>
                <td className="mono dim">{formatYen(shoe.retailPrice)}</td>
                <td className="mono cyan">{shoe.buyScore}</td>
                <td>
                  <span className={`badge badge-${shoe.liquidity === '高' ? 'green' : 'amber'}`}>
                    {shoe.liquidity}
                  </span>
                </td>
                <td>
                  <button className="btn-ghost" type="button" onClick={() => onOpenDetail(shoe.sku)}>
                    詳細
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  )
}
