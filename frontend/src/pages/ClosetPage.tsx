// file: src/pages/ClosetPage.tsx
import { useEffect, useState } from 'react'
import type { FormEvent } from 'react'
import { formatYen } from '../data/sneakers'
import { apiFetch } from '../services/api'
import type { ClosetResponse } from '../types/assets'

type ClosetFormState = {
  sku: string
  model: string
  brand: string
  quantity: string
  avgBuyPrice: string
  currentPrice: string
}

const initialForm: ClosetFormState = {
  sku: '',
  model: '',
  brand: '',
  quantity: '1',
  avgBuyPrice: '',
  currentPrice: '',
}

export function ClosetPage() {
  const [items, setItems] = useState<ClosetResponse['items']>([])
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')
  const [form, setForm] = useState<ClosetFormState>(initialForm)

  const load = async () => {
    setLoading(true)
    setError('')
    try {
      const payload = await apiFetch<ClosetResponse>('/closet')
      setItems(payload.items)
    } catch {
      setError('closet APIの取得に失敗しました。')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    void load()
  }, [])

  const onCreate = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    setSaving(true)
    setError('')
    try {
      await apiFetch('/closet', {
        method: 'POST',
        body: JSON.stringify({
          sku: form.sku,
          model: form.model,
          brand: form.brand,
          quantity: Number(form.quantity),
          avg_buy_price: Number(form.avgBuyPrice),
          current_price: Number(form.currentPrice),
        }),
      })
      setForm(initialForm)
      await load()
    } catch {
      setError('closet item の追加に失敗しました。')
    } finally {
      setSaving(false)
    }
  }

  const onIncrement = async (itemId: number, currentQuantity: number) => {
    setSaving(true)
    setError('')
    try {
      await apiFetch(`/closet/${itemId}`, {
        method: 'PATCH',
        body: JSON.stringify({ quantity: currentQuantity + 1 }),
      })
      await load()
    } catch {
      setError('closet item の更新に失敗しました。')
    } finally {
      setSaving(false)
    }
  }

  const onDelete = async (itemId: number) => {
    setSaving(true)
    setError('')
    try {
      await apiFetch(`/closet/${itemId}`, { method: 'DELETE' })
      await load()
    } catch {
      setError('closet item の削除に失敗しました。')
    } finally {
      setSaving(false)
    }
  }

  return (
    <section className="page">
      <div className="section-header">
        <h2>Digital Closet</h2>
        <span>保有スニーカー管理</span>
      </div>

      <div className="panel">
        <h3>Closet Item 追加</h3>
        <form className="form-grid" onSubmit={onCreate}>
          <label>
            SKU
            <input className="form-input" value={form.sku} onChange={(event) => setForm((current) => ({ ...current, sku: event.target.value }))} required />
          </label>
          <label>
            Model
            <input className="form-input" value={form.model} onChange={(event) => setForm((current) => ({ ...current, model: event.target.value }))} required />
          </label>
          <label>
            Brand
            <input className="form-input" value={form.brand} onChange={(event) => setForm((current) => ({ ...current, brand: event.target.value }))} required />
          </label>
          <label>
            Quantity
            <input className="form-input" inputMode="numeric" value={form.quantity} onChange={(event) => setForm((current) => ({ ...current, quantity: event.target.value }))} required />
          </label>
          <label>
            Avg Buy Price
            <input className="form-input" inputMode="numeric" value={form.avgBuyPrice} onChange={(event) => setForm((current) => ({ ...current, avgBuyPrice: event.target.value }))} required />
          </label>
          <label>
            Current Price
            <input className="form-input" inputMode="numeric" value={form.currentPrice} onChange={(event) => setForm((current) => ({ ...current, currentPrice: event.target.value }))} required />
          </label>
          <button className="btn-primary" type="submit" disabled={saving}>
            追加
          </button>
        </form>
      </div>

      <div className="panel">
        <h3>Closet 一覧</h3>
        {loading ? <p>読み込み中...</p> : null}
        {error ? <p className="form-error">{error}</p> : null}
        <table className="data-table">
          <thead>
            <tr>
              <th>SKU</th>
              <th>Model</th>
              <th>Qty</th>
              <th>Avg Buy</th>
              <th>Current</th>
              <th>Value</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            {items.map((item) => (
              <tr key={item.id}>
                <td className="mono">{item.sku}</td>
                <td>{item.model}</td>
                <td className="mono">{item.quantity}</td>
                <td className="mono">{formatYen(item.avg_buy_price)}</td>
                <td className="mono">{formatYen(item.current_price)}</td>
                <td className="mono cyan">{formatYen(item.current_price * item.quantity)}</td>
                <td>
                  <div className="row-actions">
                    <button className="btn-ghost" type="button" onClick={() => void onIncrement(item.id, item.quantity)}>
                      +1
                    </button>
                    <button className="btn-ghost" type="button" onClick={() => void onDelete(item.id)}>
                      削除
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  )
}
