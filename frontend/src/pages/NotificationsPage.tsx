// file: src/pages/NotificationsPage.tsx
import { useEffect, useState } from 'react'
import { formatYen } from '../data/sneakers'
import { apiFetch } from '../services/api'
import type { AlertDispatchResponse, NotificationCenterResponse } from '../types/notifications'

export function NotificationsPage() {
  const [items, setItems] = useState<NotificationCenterResponse['items']>([])
  const [loading, setLoading] = useState(true)
  const [running, setRunning] = useState(false)
  const [error, setError] = useState('')
  const [lastDispatch, setLastDispatch] = useState<AlertDispatchResponse | null>(null)

  const load = async () => {
    setLoading(true)
    setError('')
    try {
      const payload = await apiFetch<NotificationCenterResponse>('/notifications?limit=50')
      setItems(payload.items)
    } catch {
      setError('notification center の取得に失敗しました。')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    void load()
  }, [])

  const runDispatch = async () => {
    setRunning(true)
    setError('')
    try {
      const result = await apiFetch<AlertDispatchResponse>('/notifications/run', {
        method: 'POST',
      })
      setLastDispatch(result)
      await load()
    } catch {
      setError('alert dispatch 実行に失敗しました。')
    } finally {
      setRunning(false)
    }
  }

  return (
    <section className="page">
      <div className="section-header">
        <h2>通知センター</h2>
        <span>scheduler / dedupe / cooldown 状態を確認</span>
      </div>

      <div className="panel">
        <h3>Alert Flow Control</h3>
        <div className="panel-actions">
          <button className="btn-primary" type="button" onClick={() => void runDispatch()} disabled={running}>
            今すぐ評価実行
          </button>
          <button className="btn-ghost" type="button" onClick={() => void load()} disabled={loading}>
            再読み込み
          </button>
        </div>
        {lastDispatch ? (
          <div className="status-grid">
            <span className="mono">status: {lastDispatch.status}</span>
            <span className="mono">evaluated: {lastDispatch.evaluated}</span>
            <span className="mono">triggered: {lastDispatch.triggered}</span>
            <span className="mono">duplicates: {lastDispatch.duplicates}</span>
            <span className="mono">cooldown: {lastDispatch.cooldown_skipped}</span>
            <span className="mono">missing_market: {lastDispatch.missing_market}</span>
          </div>
        ) : null}
      </div>

      <div className="panel">
        <h3>Notification History</h3>
        {loading ? <p>読み込み中...</p> : null}
        {error ? <p className="form-error">{error}</p> : null}
        {!loading && !error && items.length === 0 ? <p>通知履歴はまだありません。</p> : null}
        <table className="data-table">
          <thead>
            <tr>
              <th>At</th>
              <th>SKU</th>
              <th>Rule</th>
              <th>Threshold</th>
              <th>Price</th>
              <th>Status</th>
              <th>Message</th>
            </tr>
          </thead>
          <tbody>
            {items.map((item) => (
              <tr key={item.id}>
                <td className="mono">{new Date(item.created_at).toLocaleString()}</td>
                <td className="mono">{item.sku}</td>
                <td className="mono">{item.rule_type}</td>
                <td className="mono">{formatYen(item.threshold)}</td>
                <td className="mono">{formatYen(item.trigger_price)}</td>
                <td>{item.status}</td>
                <td>{item.message}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  )
}
