// file: src/pages/DetailPage.tsx
import { useEffect, useMemo, useState } from 'react'
import { CultureRadarChart } from '../components/CultureRadarChart'
import { SNEAKERS, formatYen } from '../data/sneakers'
import { apiFetch } from '../services/api'

type DetailPageProps = {
  sku: string
}

const periods = ['1日', '5日', '2週', '1ヶ月', '3ヶ月', '半年', '1年'] as const

const radarValues = [0.94, 0.88, 0.91, 0.96, 0.97, 0.82, 0.68, 0.55, 0.88, 0.85, 0.9, 0.92, 0.86, 0.78, 0.99]

type DetailApiResponse = {
  item: {
    sku: string
    model: string
    brand: string
    retail_price: number
    market_price: number
    buy_score: number
    liquidity: string
    note: string
  }
}

type ImageAnalysisResponse = {
  data: {
    is_sneaker: boolean
    brand: string
    model: string
    colorway: string
    material: string
    notes: string[]
    confidence: number
  }
  source: string
  updated_at: string
  ai_available: boolean
  partial: boolean
  error_message?: string
}

export function DetailPage({ sku }: DetailPageProps) {
  const [activePeriod, setActivePeriod] = useState<(typeof periods)[number]>('1日')
  const [apiItem, setApiItem] = useState<DetailApiResponse['item'] | null>(null)
  const [error, setError] = useState('')
  const [actionMessage, setActionMessage] = useState('')
  const [analysisInput, setAnalysisInput] = useState('https://example.com/sneaker.jpg')
  const [analysis, setAnalysis] = useState<ImageAnalysisResponse | null>(null)
  const [analysisLoading, setAnalysisLoading] = useState(false)
  const [analysisError, setAnalysisError] = useState('')

  useEffect(() => {
    const controller = new AbortController()

    const load = async () => {
      setError('')
      try {
        const response = await fetch(`http://127.0.0.1:8000/api/v1/sneakers/${sku}`, {
          signal: controller.signal,
        })
        if (!response.ok) {
          throw new Error('detail failed')
        }
        const payload = (await response.json()) as DetailApiResponse
        setApiItem(payload.item)
      } catch {
        setApiItem(null)
        setError('詳細APIに接続できなかったため、ローカルデータを表示しています。')
      }
    }

    load()
    return () => controller.abort()
  }, [sku])

  const local = SNEAKERS.find((candidate) => candidate.sku === sku) ?? SNEAKERS[0]
  const sneaker = useMemo(
    () => ({
      sku: apiItem?.sku ?? local.sku,
      model: apiItem?.model ?? local.model,
      brand: apiItem?.brand ?? local.brand,
      retailPrice: apiItem?.retail_price ?? local.retailPrice,
      marketPrice: apiItem?.market_price ?? local.marketPrice,
      buyScore: apiItem?.buy_score ?? local.buyScore,
      note: apiItem?.note ?? local.note,
    }),
    [apiItem, local],
  )

  const bars = [
    ['文化的希少性', 94],
    ['市場流動性', 88],
    ['価格モメンタム', 85],
    ['SNSトレンド', 91],
    ['ブランド指数', 96],
    ['将来予測 (30日)', 78],
  ] as const

  const premium = Math.round(((sneaker.marketPrice - sneaker.retailPrice) / sneaker.retailPrice) * 100)

  const onAddWishlist = async () => {
    try {
      await apiFetch('/wishlist', {
        method: 'POST',
        body: JSON.stringify({
          sku: sneaker.sku,
          model: sneaker.model,
          brand: sneaker.brand,
          target_price: Math.max(1, sneaker.marketPrice * 0.92),
          current_price: sneaker.marketPrice,
          note: 'detail page add',
        }),
      })
      setActionMessage('Wishlistへ追加しました。')
    } catch {
      setActionMessage('Wishlist追加に失敗しました。')
    }
  }

  const onAddCloset = async () => {
    try {
      await apiFetch('/closet', {
        method: 'POST',
        body: JSON.stringify({
          sku: sneaker.sku,
          model: sneaker.model,
          brand: sneaker.brand,
          quantity: 1,
          avg_buy_price: sneaker.retailPrice,
          current_price: sneaker.marketPrice,
        }),
      })
      setActionMessage('Closetへ追加しました。')
    } catch {
      setActionMessage('Closet追加に失敗しました。')
    }
  }

  const runImageAnalysis = async () => {
    setAnalysisLoading(true)
    setAnalysisError('')
    try {
      const payload = await apiFetch<ImageAnalysisResponse>('/image-analysis/analyze', {
        method: 'POST',
        body: JSON.stringify({
          image_url: analysisInput,
          hint_text: `${sneaker.brand} ${sneaker.model} ${sneaker.sku}`,
        }),
      })
      setAnalysis(payload)
    } catch {
      setAnalysis(null)
      setAnalysisError('画像解析APIの実行に失敗しました。')
    } finally {
      setAnalysisLoading(false)
    }
  }

  return (
    <section className="page">
      <div className="section-header">
        <h2>スニーカー詳細</h2>
        <span>CultureVector + BuyScore 分析</span>
      </div>
      <div className="panel detail-hero">
        <div className="detail-image-block">
          <div className="detail-image">👟</div>
          <div className="detail-actions">
            <button className="btn-primary" type="button" onClick={() => void onAddWishlist()}>
              Wishlistへ
            </button>
            <button className="btn-ghost" type="button" onClick={() => void onAddCloset()}>
              Closetへ
            </button>
          </div>
        </div>
        <div>
          <p className="detail-brand">{sneaker.brand} // SNEAKER DETAIL</p>
          <h3>{sneaker.model}</h3>
          {error ? <p>{error}</p> : null}
          {actionMessage ? <p>{actionMessage}</p> : null}
          <div className="period-tabs">
            {periods.map((period) => (
              <button
                key={period}
                className={`period-tab ${activePeriod === period ? 'active' : ''}`}
                type="button"
                onClick={() => setActivePeriod(period)}
              >
                {period}
              </button>
            ))}
          </div>
          <svg width="100%" height="84" viewBox="0 0 600 84" aria-label="価格チャート">
            <defs>
              <linearGradient id="price-grad" x1="0" x2="0" y1="0" y2="1">
                <stop offset="0%" stopColor="#00c8ff" stopOpacity="0.25" />
                <stop offset="100%" stopColor="#00c8ff" stopOpacity="0" />
              </linearGradient>
            </defs>
            <path
              d="M0,60 L60,50 L120,54 L180,38 L240,42 L300,28 L360,22 L420,26 L480,14 L540,10 L600,8"
              fill="none"
              stroke="#00c8ff"
              strokeWidth="2"
            />
            <path
              d="M0,60 L60,50 L120,54 L180,38 L240,42 L300,28 L360,22 L420,26 L480,14 L540,10 L600,8 L600,84 L0,84Z"
              fill="url(#price-grad)"
            />
          </svg>
        </div>
      </div>

      <div className="detail-stats">
        <div>市場価格: {formatYen(sneaker.marketPrice)}</div>
        <div>定価: {formatYen(sneaker.retailPrice)}</div>
        <div>プレミアム率: {premium > 0 ? '+' : ''}{premium}%</div>
        <div>BuyScore: {sneaker.buyScore}</div>
      </div>

      <div className="panel-grid">
        <div className="panel">
          <h3>CultureVector — 15次元分析</h3>
          <CultureRadarChart values={radarValues} />
        </div>

        <div className="panel">
          <h3>BuyScore 内訳</h3>
          <div className="score-chip">{sneaker.buyScore}/100</div>
          <div className="score-list">
            {bars.map(([label, value]) => (
              <div key={label} className="score-row">
                <div className="score-label">
                  <span>{label}</span>
                  <span>{value}</span>
                </div>
                <div className="score-bg">
                  <div className="score-fill" style={{ width: `${value}%` }} />
                </div>
              </div>
            ))}
          </div>
          <p className="insight-box">
            {activePeriod}基準で、{sneaker.model} は文化的希少性とSNSトレンドが強く、短中期では買い優勢です。
          </p>
        </div>
      </div>

      <div className="panel">
        <h3>画像解析結果</h3>
        <label className="form-label" htmlFor="analysis-input">
          Image URL
        </label>
        <input
          id="analysis-input"
          className="form-input"
          value={analysisInput}
          onChange={(event) => setAnalysisInput(event.target.value)}
        />
        <p>
          <button className="btn-ghost" type="button" onClick={() => void runImageAnalysis()}>
            画像解析を実行
          </button>
        </p>
        {analysisLoading ? <p>画像解析中...</p> : null}
        {analysisError ? <p className="form-error">{analysisError}</p> : null}
        {!analysisLoading && !analysisError && !analysis ? <p>未実行</p> : null}
        {analysis ? (
          <>
            <p>
              sneaker: {String(analysis.data.is_sneaker)} / confidence:{' '}
              {analysis.data.confidence.toFixed(2)}
            </p>
            <p>
              brand: {analysis.data.brand} / model: {analysis.data.model} / colorway:{' '}
              {analysis.data.colorway}
            </p>
            <p>
              source: {analysis.source} / partial: {String(analysis.partial)} / ai_available:{' '}
              {String(analysis.ai_available)}
            </p>
            {analysis.error_message ? <p className="form-error">{analysis.error_message}</p> : null}
            {analysis.data.notes.length > 0 ? (
              <ul>
                {analysis.data.notes.map((note) => (
                  <li key={note}>{note}</li>
                ))}
              </ul>
            ) : (
              <p>notesなし</p>
            )}
          </>
        ) : null}
      </div>
    </section>
  )
}
