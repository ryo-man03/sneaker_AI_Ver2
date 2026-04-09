// file: src/pages/MarketPage.tsx
import { useEffect, useState } from 'react'
import { formatYen } from '../data/sneakers'

type MarketItem = {
  sku: string
  ask_price: number
  bid_price: number
  spread_pct: number
  last_sale: number
  liquidity: string
}

type MarketResponse = {
  items: MarketItem[]
}

export function MarketPage() {
  const [rows, setRows] = useState<MarketItem[]>([])
  const [error, setError] = useState('')

  useEffect(() => {
    const controller = new AbortController()

    const run = async () => {
      setError('')
      try {
        const response = await fetch('http://127.0.0.1:8000/api/v1/market?period=1d', {
          signal: controller.signal,
        })
        if (!response.ok) {
          throw new Error('market failed')
        }
        const payload = (await response.json()) as MarketResponse
        setRows(payload.items)
      } catch {
        setRows([])
        setError('market API取得に失敗しました。')
      }
    }

    run()
    return () => controller.abort()
  }, [])

  return (
    <section className="page">
      <div className="section-header">
        <h2>市場価格 / 相場</h2>
        <span>Core Data API</span>
      </div>
      <div className="panel">
        <h3>Ask / Bid / Spread</h3>
        {error ? <p>{error}</p> : null}
        <table className="data-table">
          <thead>
            <tr>
              <th>SKU</th>
              <th>Ask</th>
              <th>Bid</th>
              <th>Spread</th>
              <th>Last Sale</th>
              <th>流動性</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((row) => (
              <tr key={row.sku}>
                <td className="mono">{row.sku}</td>
                <td className="mono cyan">{formatYen(row.ask_price)}</td>
                <td className="mono">{formatYen(row.bid_price)}</td>
                <td className="mono">{row.spread_pct}%</td>
                <td className="mono">{formatYen(row.last_sale)}</td>
                <td>{row.liquidity}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  )
}
