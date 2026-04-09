// file: src/data/sneakers.ts
export type SneakerRecord = {
  model: string
  brand: string
  sku: string
  marketPrice: number
  retailPrice: number
  buyScore: number
  liquidity: '高' | '中' | '低'
  trendPct: number
  note: string
}

export const SNEAKERS: SneakerRecord[] = [
  {
    model: 'Air Jordan 1 Retro High OG "Bred"',
    brand: 'NIKE',
    sku: '555088-001',
    marketPrice: 48500,
    retailPrice: 16500,
    buyScore: 89,
    liquidity: '高',
    trendPct: 12.4,
    note: '2024 Restock',
  },
  {
    model: 'Yeezy Boost 350 V2 "Onyx"',
    brand: 'ADIDAS',
    sku: 'HQ4540',
    marketPrice: 32000,
    retailPrice: 27500,
    buyScore: 62,
    liquidity: '中',
    trendPct: -3.1,
    note: '明日発売予定',
  },
  {
    model: 'New Balance 9060 "Sea Salt"',
    brand: 'NEW BALANCE',
    sku: 'U9060AAA',
    marketPrice: 21000,
    retailPrice: 19800,
    buyScore: 77,
    liquidity: '高',
    trendPct: 5.8,
    note: '在庫あり',
  },
  {
    model: 'Nike Dunk Low "Panda"',
    brand: 'NIKE',
    sku: 'DD1391-100',
    marketPrice: 22800,
    retailPrice: 13200,
    buyScore: 81,
    liquidity: '高',
    trendPct: 2.1,
    note: '定番モデル',
  },
  {
    model: 'Asics Gel-Kayano 14',
    brand: 'ASICS',
    sku: '1201A019',
    marketPrice: 28000,
    retailPrice: 16500,
    buyScore: 91,
    liquidity: '高',
    trendPct: 7.3,
    note: 'Y2K復刻',
  },
]

export function formatYen(amount: number): string {
  return `¥${amount.toLocaleString('ja-JP')}`
}
