// file: src/types/notifications.ts
import type { ApiMeta } from '../services/api'

export type NotificationEvent = {
  id: number
  rule_id: number
  sku: string
  rule_type: string
  threshold: number
  trigger_price: number
  dedupe_key: string
  channel: string
  status: string
  message: string
  created_at: string
}

export type NotificationCenterResponse = {
  items: NotificationEvent[]
  meta: ApiMeta
}

export type AlertDispatchResponse = {
  status: string
  evaluated: number
  triggered: number
  duplicates: number
  cooldown_skipped: number
  missing_market: number
  scheduler_running: boolean
  interval_seconds: number
  meta: ApiMeta
}
