// file: src/types/intelligence.ts
import type { ApiMeta } from '../services/api'

export type CultureVectorPoint = {
  label: string
  score: number
}

export type BuyScoreComponents = {
  market_momentum: number
  liquidity: number
  stock_correlation: number
  culture_signal: number
  risk_penalty: number
}

export type BuyScoreResponse = {
  sku: string
  model: string
  brand: string
  buy_score: number
  fallback_reason: string | null
  components: BuyScoreComponents
  culture_vector: CultureVectorPoint[]
  meta: ApiMeta
}

export type CorrelationItem = {
  ticker: string
  company: string
  correlation: number
  relation: 'positive' | 'negative'
  change_pct: number
  index_change_pct: number
}

export type CorrelationResponse = {
  period: string
  items: CorrelationItem[]
  summary: string
  meta: ApiMeta
}

export type IntakeType = 'image' | 'url' | 'csv'

export type IntakePreviewItem = {
  sku: string
  model: string
  hint: string
}

export type IntakeResponse = {
  intake_type: IntakeType
  parsed_items: number
  accepted: boolean
  preview: IntakePreviewItem[]
  warnings: string[]
  meta: ApiMeta
}