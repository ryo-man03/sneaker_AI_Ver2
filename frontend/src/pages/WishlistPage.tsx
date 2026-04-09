// file: src/pages/WishlistPage.tsx
import { useEffect, useState } from 'react'
import type { FormEvent } from 'react'
import { formatYen } from '../data/sneakers'
import { apiFetch } from '../services/api'
import type { PriceAlertResponse, WishlistResponse } from '../types/assets'

type WishlistFormState = {
  sku: string
  model: string
  brand: string
  targetPrice: string
  currentPrice: string
  note: string
}

type AlertFormState = {
  sku: string
  threshold: string
  cooldown: string
}

const initialWishlistForm: WishlistFormState = {
  sku: '',
  model: '',
  brand: '',
  targetPrice: '',
  currentPrice: '',
  note: '',
}

const initialAlertForm: AlertFormState = {
  sku: '',
  threshold: '',
  cooldown: '180',
}

export function WishlistPage() {
  const [wishlist, setWishlist] = useState<WishlistResponse['items']>([])
  const [alerts, setAlerts] = useState<PriceAlertResponse['items']>([])
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')
  const [wishlistForm, setWishlistForm] = useState<WishlistFormState>(initialWishlistForm)
  const [alertForm, setAlertForm] = useState<AlertFormState>(initialAlertForm)

  const load = async () => {
    setLoading(true)
    setError('')
    try {
      const [wishlistPayload, alertPayload] = await Promise.all([
        apiFetch<WishlistResponse>('/wishlist'),
        apiFetch<PriceAlertResponse>('/price-alerts'),
      ])
      setWishlist(wishlistPayload.items)
      setAlerts(alertPayload.items)
      setAlertForm((current) => ({
        ...current,
        sku: current.sku || wishlistPayload.items[0]?.sku || '',
      }))
    } catch {
      setError('wishlist/alerts APIの取得に失敗しました。')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    void load()
  }, [])

  const onCreateWishlist = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    setSaving(true)
    setError('')
    try {
      await apiFetch('/wishlist', {
        method: 'POST',
        body: JSON.stringify({
          sku: wishlistForm.sku,
          model: wishlistForm.model,
          brand: wishlistForm.brand,
          target_price: Number(wishlistForm.targetPrice),
          current_price: Number(wishlistForm.currentPrice),
          note: wishlistForm.note,
        }),
      })
      setWishlistForm(initialWishlistForm)
      await load()
    } catch {
      setError('wishlist item の作成に失敗しました。')
    } finally {
      setSaving(false)
    }
  }

  const onDeleteWishlist = async (itemId: number) => {
    setSaving(true)
    setError('')
    try {
      await apiFetch(`/wishlist/${itemId}`, { method: 'DELETE' })
      await load()
    } catch {
      setError('wishlist item の削除に失敗しました。')
    } finally {
      setSaving(false)
    }
  }

  const onCreateAlert = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    setSaving(true)
    setError('')
    try {
      await apiFetch('/price-alerts', {
        method: 'POST',
        body: JSON.stringify({
          sku: alertForm.sku,
          rule_type: 'price_below',
          threshold: Number(alertForm.threshold),
          active: true,
          cooldown_minutes: Number(alertForm.cooldown),
        }),
      })
      setAlertForm((current) => ({ ...current, threshold: '' }))
      await load()
    } catch {
      setError('price alert rule の保存に失敗しました。')
    } finally {
      setSaving(false)
    }
  }

  const onToggleAlert = async (ruleId: number, active: boolean) => {
    setSaving(true)
    setError('')
    try {
      await apiFetch(`/price-alerts/${ruleId}`, {
        method: 'PATCH',
        body: JSON.stringify({ active: !active }),
      })
      await load()
    } catch {
      setError('price alert rule の更新に失敗しました。')
    } finally {
      setSaving(false)
    }
  }

  return (
    <section className="page">
      <div className="section-header">
        <h2>ウィッシュリスト</h2>
        <span>価格追跡 + アラート条件管理</span>
      </div>

      <div className="panel-grid">
        <div className="panel">
          <h3>Wishlist Item 追加</h3>
          <form className="form-grid" onSubmit={onCreateWishlist}>
            <label>
              SKU
              <input
                className="form-input"
                value={wishlistForm.sku}
                onChange={(event) => setWishlistForm((current) => ({ ...current, sku: event.target.value }))}
                required
              />
            </label>
            <label>
              Model
              <input
                className="form-input"
                value={wishlistForm.model}
                onChange={(event) => setWishlistForm((current) => ({ ...current, model: event.target.value }))}
                required
              />
            </label>
            <label>
              Brand
              <input
                className="form-input"
                value={wishlistForm.brand}
                onChange={(event) => setWishlistForm((current) => ({ ...current, brand: event.target.value }))}
                required
              />
            </label>
            <label>
              Target Price
              <input
                className="form-input"
                inputMode="numeric"
                value={wishlistForm.targetPrice}
                onChange={(event) => setWishlistForm((current) => ({ ...current, targetPrice: event.target.value }))}
                required
              />
            </label>
            <label>
              Current Price
              <input
                className="form-input"
                inputMode="numeric"
                value={wishlistForm.currentPrice}
                onChange={(event) => setWishlistForm((current) => ({ ...current, currentPrice: event.target.value }))}
                required
              />
            </label>
            <label>
              Note
              <input
                className="form-input"
                value={wishlistForm.note}
                onChange={(event) => setWishlistForm((current) => ({ ...current, note: event.target.value }))}
              />
            </label>
            <button className="btn-primary" type="submit" disabled={saving}>
              追加
            </button>
          </form>
        </div>

        <div className="panel">
          <h3>Price Alert Rule 保存</h3>
          <form className="form-grid" onSubmit={onCreateAlert}>
            <label>
              SKU
              <input
                className="form-input"
                value={alertForm.sku}
                onChange={(event) => setAlertForm((current) => ({ ...current, sku: event.target.value }))}
                placeholder="例: 555088-001"
                required
              />
            </label>
            <label>
              Threshold
              <input
                className="form-input"
                inputMode="numeric"
                value={alertForm.threshold}
                onChange={(event) => setAlertForm((current) => ({ ...current, threshold: event.target.value }))}
                required
              />
            </label>
            <label>
              Cooldown(min)
              <input
                className="form-input"
                inputMode="numeric"
                value={alertForm.cooldown}
                onChange={(event) => setAlertForm((current) => ({ ...current, cooldown: event.target.value }))}
                required
              />
            </label>
            <button className="btn-primary" type="submit" disabled={saving}>
              ルール保存
            </button>
          </form>
        </div>
      </div>

      <div className="panel">
        <h3>Wishlist 一覧</h3>
        {loading ? <p>読み込み中...</p> : null}
        {error ? <p className="form-error">{error}</p> : null}
        <table className="data-table">
          <thead>
            <tr>
              <th>SKU</th>
              <th>Model</th>
              <th>Target</th>
              <th>Current</th>
              <th>Gap</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            {wishlist.map((item) => {
              const gap = item.current_price - item.target_price
              return (
                <tr key={item.id}>
                  <td className="mono">{item.sku}</td>
                  <td>{item.model}</td>
                  <td className="mono">{formatYen(item.target_price)}</td>
                  <td className="mono">{formatYen(item.current_price)}</td>
                  <td className={`mono ${gap <= 0 ? 'cyan' : ''}`}>{formatYen(gap)}</td>
                  <td>
                    <button className="btn-ghost" type="button" onClick={() => void onDeleteWishlist(item.id)}>
                      削除
                    </button>
                  </td>
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>

      <div className="panel">
        <h3>Price Alert Rules</h3>
        <table className="data-table">
          <thead>
            <tr>
              <th>SKU</th>
              <th>Type</th>
              <th>Threshold</th>
              <th>Cooldown</th>
              <th>Status</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            {alerts.map((rule) => (
              <tr key={rule.id}>
                <td className="mono">{rule.sku}</td>
                <td className="mono">{rule.rule_type}</td>
                <td className="mono">{formatYen(rule.threshold)}</td>
                <td className="mono">{rule.cooldown_minutes}m</td>
                <td>{rule.active ? 'active' : 'paused'}</td>
                <td>
                  <button
                    className="btn-ghost"
                    type="button"
                    onClick={() => void onToggleAlert(rule.id, rule.active)}
                  >
                    {rule.active ? '停止' : '再開'}
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
