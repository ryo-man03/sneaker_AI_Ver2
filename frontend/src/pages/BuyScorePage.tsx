// file: src/pages/BuyScorePage.tsx
import { useEffect, useMemo, useState } from 'react'
import { CultureRadarChart } from '../components/CultureRadarChart'
import { SNEAKERS } from '../data/sneakers'
import { apiFetch } from '../services/api'
import type { BuyScoreResponse } from '../types/intelligence'

const defaultSku = SNEAKERS[0]?.sku ?? '555088-001'

export function BuyScorePage() {
  const [sku, setSku] = useState(defaultSku)
  const [payload, setPayload] = useState<BuyScoreResponse | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const load = async (targetSku: string) => {
    setLoading(true)
    setError('')
    try {
      const response = await apiFetch<BuyScoreResponse>(`/intelligence/buyscore/${targetSku}`)
      setPayload(response)
    } catch {
      setPayload(null)
      setError('BuyScore API の取得に失敗しました。')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    void load(sku)
  }, [sku])

  const radarValues = useMemo(() => {
    if (!payload) {
      return new Array<number>(15).fill(0.35)
    }
    return payload.culture_vector.map((item) => item.score)
  }, [payload])

  return (
    <section className="page">
      <div className="section-header">
        <h2>BuyScore 調整</h2>
        <span>AI / Intelligence</span>
      </div>

      <div className="panel">
        <h3>スコア再計算</h3>
        <label className="form-label" htmlFor="buyscore-sku">
          SKU
        </label>
        <select id="buyscore-sku" className="filter-select" value={sku} onChange={(event) => setSku(event.target.value)}>
          {SNEAKERS.map((item) => (
            <option key={item.sku} value={item.sku}>
              {item.sku} / {item.model}
            </option>
          ))}
        </select>
        <p>
          <button className="btn-primary" type="button" onClick={() => void load(sku)}>
            再計算
          </button>
        </p>
        {loading ? <p>再計算中...</p> : null}
        {error ? <p>{error}</p> : null}
      </div>

      <div className="panel-grid">
        <div className="panel">
          <h3>総合 BuyScore</h3>
          {payload ? (
            <>
              <div className="score-chip">{payload.buy_score}/100</div>
              <p>
                {payload.brand} / {payload.model}
              </p>
              {payload.fallback_reason ? <p>{payload.fallback_reason}</p> : null}
              {payload.meta.partial ? <p>partial mode: ON</p> : <p>partial mode: OFF</p>}
            </>
          ) : (
            <p>データ未取得</p>
          )}
        </div>

        <div className="panel">
          <h3>CultureVector</h3>
          <CultureRadarChart values={radarValues} />
        </div>
      </div>

      <div className="panel">
        <h3>内訳</h3>
        {payload ? (
          <table className="data-table">
            <thead>
              <tr>
                <th>Factor</th>
                <th>Value</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td>market_momentum</td>
                <td className="mono">{payload.components.market_momentum}</td>
              </tr>
              <tr>
                <td>liquidity</td>
                <td className="mono">{payload.components.liquidity}</td>
              </tr>
              <tr>
                <td>stock_correlation</td>
                <td className="mono">{payload.components.stock_correlation}</td>
              </tr>
              <tr>
                <td>culture_signal</td>
                <td className="mono">{payload.components.culture_signal}</td>
              </tr>
              <tr>
                <td>risk_penalty</td>
                <td className="mono">-{payload.components.risk_penalty}</td>
              </tr>
            </tbody>
          </table>
        ) : (
          <p>データ未取得</p>
        )}
      </div>
    </section>
  )
}