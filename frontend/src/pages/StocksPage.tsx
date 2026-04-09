// file: src/pages/StocksPage.tsx
import { useEffect, useState } from 'react'

type StockItem = {
  ticker: string
  company: string
  price: number
  change_pct: number
  direction: string
  index_name: string
  index_change_pct: number
}

type StocksResponse = {
  items: StockItem[]
  correlations_summary: string
}

export function StocksPage() {
  const [rows, setRows] = useState<StockItem[]>([])
  const [summary, setSummary] = useState('')
  const [error, setError] = useState('')

  useEffect(() => {
    const controller = new AbortController()

    const run = async () => {
      setError('')
      try {
        const response = await fetch('http://127.0.0.1:8000/api/v1/stocks?period=1d', {
          signal: controller.signal,
        })
        if (!response.ok) {
          throw new Error('stocks failed')
        }
        const payload = (await response.json()) as StocksResponse
        setRows(payload.items)
        setSummary(payload.correlations_summary)
      } catch {
        setRows([])
        setSummary('')
        setError('stocks API取得に失敗しました。')
      }
    }

    run()
    return () => controller.abort()
  }, [])

  return (
    <section className="page">
      <div className="section-header">
        <h2>株価監視</h2>
        <span>Core Data API</span>
      </div>
      <div className="panel">
        <h3>関連企業スナップショット</h3>
        {error ? <p>{error}</p> : null}
        <table className="data-table">
          <thead>
            <tr>
              <th>Ticker</th>
              <th>Company</th>
              <th>Price</th>
              <th>Change</th>
              <th>Index</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((row) => (
              <tr key={row.ticker}>
                <td className="mono">{row.ticker}</td>
                <td>{row.company}</td>
                <td className="mono">${row.price.toFixed(1)}</td>
                <td className={`mono ${row.direction === 'up' ? 'cyan' : ''}`}>{row.change_pct}%</td>
                <td className="mono">{row.index_name} ({row.index_change_pct}%)</td>
              </tr>
            ))}
          </tbody>
        </table>
        {summary ? <p>{summary}</p> : null}
      </div>
    </section>
  )
}
