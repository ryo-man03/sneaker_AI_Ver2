import { useEffect, useState } from 'react'
import { apiFetch } from '../services/api'

type AdminOpsResponse = {
  data: {
    db_counts: {
      sneakers: number
      market_snapshots: number
      stock_snapshots: number
      wishlist_items: number
      closet_items: number
      price_alert_rules: number
      notification_events: number
    }
    scheduler: {
      running: boolean
      interval_seconds: number
    }
    integrations: {
      gemini_configured: boolean
      instagram_configured: boolean
    }
    hardening?: {
      lifespan_mode: string
      security_headers_enabled: boolean
      trusted_hosts: string[]
    }
    maintenance?: {
      key_rotation_days: number
      dependency_audit_days: number
      release_channel: string
    }
    dqm: {
      passed: boolean
      stale_count: number
      checks: Array<{
        key: string
        ok: boolean
        detail: string
      }>
    }
  }
  source: string
  updated_at: string
  ai_available: boolean
  partial: boolean
  error_message?: string
}

export function AdminPage() {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [reliability, setReliability] = useState<AdminOpsResponse | null>(null)

  const loadReliability = async () => {
    setLoading(true)
    setError('')
    try {
      const response = await apiFetch<AdminOpsResponse>('/admin-ops/reliability')
      setReliability(response)
    } catch {
      setError('AdminOps reliability API の取得に失敗しました。')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    void loadReliability()
  }, [])

  return (
    <section className="page">
      <div className="section-header">
        <h2>管理コンソール</h2>
        <span>Reliability / AdminOps</span>
      </div>

      <div className="panel">
        <h3>Reliability Snapshot</h3>
        <p>
          <button className="btn-ghost" type="button" onClick={() => void loadReliability()}>
            再取得
          </button>
        </p>

        {loading ? <p>読み込み中...</p> : null}
        {error ? <p className="form-error">{error}</p> : null}
        {!loading && !error && !reliability ? <p>未取得</p> : null}

        {reliability ? (
          <>
            <p>
              source: {reliability.source} / partial: {String(reliability.partial)} / updated:{' '}
              {new Date(reliability.updated_at).toLocaleString('ja-JP')}
            </p>
            {reliability.error_message ? <p className="form-error">{reliability.error_message}</p> : null}
            <div className="detail-stats">
              <div>sneakers: {reliability.data.db_counts.sneakers}</div>
              <div>market: {reliability.data.db_counts.market_snapshots}</div>
              <div>stocks: {reliability.data.db_counts.stock_snapshots}</div>
              <div>alert-rules: {reliability.data.db_counts.price_alert_rules}</div>
              <div>notifications: {reliability.data.db_counts.notification_events}</div>
              <div>
                scheduler: {reliability.data.scheduler.running ? 'running' : 'stopped'} (
                {reliability.data.scheduler.interval_seconds}s)
              </div>
            </div>

            <h4>DQM</h4>
            <p>
              passed: {String(reliability.data.dqm.passed)} / stale_count: {reliability.data.dqm.stale_count}
            </p>
            <ul>
              {reliability.data.dqm.checks.map((check) => (
                <li key={check.key}>
                  {check.key}: {check.ok ? 'OK' : 'NG'} / {check.detail}
                </li>
              ))}
            </ul>

            <h4>External Integrations</h4>
            <p>gemini_configured: {String(reliability.data.integrations.gemini_configured)}</p>
            <p>instagram_configured: {String(reliability.data.integrations.instagram_configured)}</p>

            <h4>Hardening</h4>
            <p>lifespan_mode: {reliability.data.hardening?.lifespan_mode ?? 'unknown'}</p>
            <p>
              security_headers_enabled:{' '}
              {String(reliability.data.hardening?.security_headers_enabled ?? false)}
            </p>
            <p>trusted_hosts: {reliability.data.hardening?.trusted_hosts.join(', ') || 'none'}</p>

            <h4>Maintenance</h4>
            <p>release_channel: {reliability.data.maintenance?.release_channel ?? 'unknown'}</p>
            <p>
              key_rotation_days: {String(reliability.data.maintenance?.key_rotation_days ?? 0)}
            </p>
            <p>
              dependency_audit_days: {String(reliability.data.maintenance?.dependency_audit_days ?? 0)}
            </p>
          </>
        ) : null}
      </div>
    </section>
  )
}
