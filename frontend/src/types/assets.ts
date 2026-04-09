// file: src/types/assets.ts
import type { ApiMeta } from '../services/api'

export type WishlistItem = {
  id: number
  sku: string
  model: string
  brand: string
  target_price: number
  current_price: number
  note: string
  created_at: string
}

export type ClosetItem = {
  id: number
  sku: string
  model: string
  brand: string
  quantity: number
  avg_buy_price: number
  current_price: number
  acquired_at: string
}

export type PriceAlertRule = {
  id: number
  sku: string
  rule_type: string
  threshold: number
  active: boolean
  cooldown_minutes: number
  last_triggered_at: string | null
  created_at: string
}

export type WishlistResponse = {
  items: WishlistItem[]
  meta: ApiMeta
}

export type ClosetResponse = {
  items: ClosetItem[]
  meta: ApiMeta
}

export type PriceAlertResponse = {
  items: PriceAlertRule[]
  meta: ApiMeta
}

export type PortfolioHolding = {
  id: number
  sku: string
  model: string
  quantity: number
  total_cost: number
  current_value: number
  unrealized_pnl: number
  roi_pct: number
}

export type PortfolioResponse = {
  total_cost: number
  current_value: number
  unrealized_pnl: number
  roi_pct: number
  holdings: PortfolioHolding[]
  meta: ApiMeta
}
