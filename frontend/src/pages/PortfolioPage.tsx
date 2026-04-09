// file: src/pages/PortfolioPage.tsx
import { useEffect, useState } from 'react'
import { formatYen } from '../data/sneakers'
import { apiFetch } from '../services/api'
import type { PortfolioResponse } from '../types/assets'

export function PortfolioPage() {
  const [portfolio, setPortfolio] = useState<PortfolioResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    const run = async () => {
      setLoading(true)
      setError('')
      try {
        const payload = await apiFetch<PortfolioResponse>('/portfolio')
        setPortfolio(payload)
      } catch {
        setPortfolio(null)
        setError('portfolio APIの取得に失敗しました。')
      } finally {
        setLoading(false)
      }
    }

    void run()
  }, [])

  return (
    <section className="page">
      <div className="section-header">
        <h2>Portfolio</h2>
        <span>資産価値 / ROI</span>
      </div>

      {loading ? <p>読み込み中...</p> : null}
      {error ? <p className="form-error">{error}</p> : null}

      {portfolio ? (
        <>
          <div className="kpi-grid">
            <article className="kpi-card cyan">
              <div>Total Cost</div>
              <strong>{formatYen(portfolio.total_cost)}</strong>
            </article>
            <article className="kpi-card green">
              <div>Current Value</div>
              <strong>{formatYen(portfolio.current_value)}</strong>
            </article>
            <article className="kpi-card amber">
              <div>Unrealized PnL</div>
              <strong>{formatYen(portfolio.unrealized_pnl)}</strong>
            </article>
            <article className="kpi-card red">
              <div>ROI</div>
              <strong>{portfolio.roi_pct}%</strong>
            </article>
          </div>

          <div className="panel">
            <h3>Holdings</h3>
            <table className="data-table">
              <thead>
                <tr>
                  <th>SKU</th>
                  <th>Model</th>
                  <th>Qty</th>
                  <th>Cost</th>
                  <th>Value</th>
                  <th>PnL</th>
                  <th>ROI</th>
                </tr>
              </thead>
              <tbody>
                {portfolio.holdings.map((holding) => (
                  <tr key={holding.id}>
                    <td className="mono">{holding.sku}</td>
                    <td>{holding.model}</td>
                    <td className="mono">{holding.quantity}</td>
                    <td className="mono">{formatYen(holding.total_cost)}</td>
                    <td className="mono">{formatYen(holding.current_value)}</td>
                    <td className={`mono ${holding.unrealized_pnl >= 0 ? 'cyan' : ''}`}>
                      {formatYen(holding.unrealized_pnl)}
                    </td>
                    <td className="mono">{holding.roi_pct}%</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      ) : null}
    </section>
  )
}
