// file: src/pages/DataOpsPage.tsx
import { useEffect, useState } from 'react'
import { apiFetch } from '../services/api'
import type { CorrelationResponse, IntakeResponse, IntakeType } from '../types/intelligence'

const csvSample = 'sku,model\n555088-001,Jordan 1 Bred\nU9060AAA,NB 9060 Sea Salt\n'

type InstagramTrendResponse = {
  data: {
    query: string
    total: number
    items: Array<{
      hashtag: string
      caption: string
      media_type: string
      permalink: string
      engagement_score: number
      observed_at: string
    }>
  }
  source: string
  updated_at: string
  ai_available: boolean
  partial: boolean
  error_message?: string
}

export function DataOpsPage() {
  const [intakeType, setIntakeType] = useState<IntakeType>('csv')
  const [payloadInput, setPayloadInput] = useState(csvSample)
  const [fileName, setFileName] = useState('batch.csv')
  const [intake, setIntake] = useState<IntakeResponse | null>(null)
  const [correlation, setCorrelation] = useState<CorrelationResponse | null>(null)
  const [loadingIntake, setLoadingIntake] = useState(false)
  const [loadingCorrelation, setLoadingCorrelation] = useState(false)
  const [loadingInstagram, setLoadingInstagram] = useState(false)
  const [instagramHashtag, setInstagramHashtag] = useState('sneakers')
  const [instagram, setInstagram] = useState<InstagramTrendResponse | null>(null)
  const [error, setError] = useState('')

  const loadCorrelation = async () => {
    setLoadingCorrelation(true)
    try {
      const response = await apiFetch<CorrelationResponse>('/intelligence/correlation?period=1d')
      setCorrelation(response)
    } catch {
      setCorrelation(null)
      setError('correlation API の取得に失敗しました。')
    } finally {
      setLoadingCorrelation(false)
    }
  }

  useEffect(() => {
    void loadCorrelation()
  }, [])

  const loadInstagramTrends = async () => {
    setLoadingInstagram(true)
    setError('')
    try {
      const response = await apiFetch<InstagramTrendResponse>(
        `/instagram/trends?hashtag=${encodeURIComponent(instagramHashtag)}&limit=5`,
      )
      setInstagram(response)
    } catch {
      setInstagram(null)
      setError('instagram trend API の取得に失敗しました。')
    } finally {
      setLoadingInstagram(false)
    }
  }

  const runIntake = async () => {
    setLoadingIntake(true)
    setError('')
    try {
      const response = await apiFetch<IntakeResponse>('/intelligence/intake', {
        method: 'POST',
        body: JSON.stringify({
          intake_type: intakeType,
          payload: payloadInput,
          file_name: fileName || undefined,
        }),
      })
      setIntake(response)
    } catch {
      setIntake(null)
      setError('intake API の実行に失敗しました。')
    } finally {
      setLoadingIntake(false)
    }
  }

  return (
    <section className="page">
      <div className="section-header">
        <h2>データ収集 / AI</h2>
        <span>image / url / csv intake + correlation</span>
      </div>

      <div className="panel-grid">
        <div className="panel">
          <h3>Intake Pipeline</h3>
          <label className="form-label" htmlFor="intake-type">
            Intake Type
          </label>
          <select
            id="intake-type"
            className="filter-select"
            value={intakeType}
            onChange={(event) => {
              const next = event.target.value as IntakeType
              setIntakeType(next)
              if (next === 'csv') {
                setPayloadInput(csvSample)
              }
              if (next === 'url') {
                setPayloadInput('https://example.com/sneaker/launch')
              }
              if (next === 'image') {
                setPayloadInput('https://example.com/image/sneaker.png')
              }
            }}
          >
            <option value="csv">csv</option>
            <option value="url">url</option>
            <option value="image">image</option>
          </select>

          <label className="form-label" htmlFor="intake-file-name">
            File Name
          </label>
          <input
            id="intake-file-name"
            className="form-input"
            value={fileName}
            onChange={(event) => setFileName(event.target.value)}
          />

          <label className="form-label" htmlFor="intake-payload">
            Payload
          </label>
          <textarea
            id="intake-payload"
            className="form-input"
            rows={7}
            value={payloadInput}
            onChange={(event) => setPayloadInput(event.target.value)}
          />

          <p>
            <button className="btn-primary" type="button" onClick={() => void runIntake()}>
              取り込み実行
            </button>
          </p>

          {loadingIntake ? <p>取り込み中...</p> : null}
          {error ? <p>{error}</p> : null}
          {intake ? (
            <>
              <p>
                accepted: {String(intake.accepted)} / parsed_items: {intake.parsed_items}
              </p>
              <table className="data-table">
                <thead>
                  <tr>
                    <th>SKU</th>
                    <th>Model</th>
                    <th>Hint</th>
                  </tr>
                </thead>
                <tbody>
                  {intake.preview.map((item) => (
                    <tr key={`${item.sku}-${item.hint}`}>
                      <td className="mono">{item.sku}</td>
                      <td>{item.model}</td>
                      <td>{item.hint}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
              {intake.warnings.length > 0 ? (
                <div>
                  {intake.warnings.map((warning) => (
                    <p key={warning}>{warning}</p>
                  ))}
                </div>
              ) : null}
            </>
          ) : null}
        </div>

        <div className="panel">
          <h3>Correlation Summary</h3>
          <p>
            <button className="btn-ghost" type="button" onClick={() => void loadCorrelation()}>
              再取得
            </button>
          </p>
          {loadingCorrelation ? <p>相関計算中...</p> : null}
          {correlation ? (
            <>
              <p>{correlation.summary}</p>
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Ticker</th>
                    <th>Company</th>
                    <th>Corr</th>
                    <th>Change%</th>
                    <th>Index%</th>
                  </tr>
                </thead>
                <tbody>
                  {correlation.items.map((item) => (
                    <tr key={item.ticker}>
                      <td className="mono">{item.ticker}</td>
                      <td>{item.company}</td>
                      <td className="mono">{item.correlation.toFixed(3)}</td>
                      <td className="mono">{item.change_pct.toFixed(2)}</td>
                      <td className="mono">{item.index_change_pct.toFixed(2)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </>
          ) : (
            <p>データ未取得</p>
          )}
        </div>

        <div className="panel">
          <h3>Instagram Trend Source</h3>
          <label className="form-label" htmlFor="instagram-hashtag">
            Hashtag
          </label>
          <input
            id="instagram-hashtag"
            className="form-input"
            value={instagramHashtag}
            onChange={(event) => setInstagramHashtag(event.target.value)}
          />
          <p>
            <button className="btn-ghost" type="button" onClick={() => void loadInstagramTrends()}>
              取得
            </button>
          </p>
          {loadingInstagram ? <p>instagram trends 取得中...</p> : null}
          {!loadingInstagram && !instagram ? <p>未取得</p> : null}
          {instagram ? (
            <>
              <p>
                source: {instagram.source} / partial: {String(instagram.partial)} / available:{' '}
                {String(instagram.ai_available)}
              </p>
              {instagram.error_message ? <p className="form-error">{instagram.error_message}</p> : null}
              {instagram.data.items.length === 0 ? <p>itemなし</p> : null}
              <ul>
                {instagram.data.items.map((item) => (
                  <li key={`${item.hashtag}-${item.observed_at}`}>
                    {item.hashtag} / score:{item.engagement_score.toFixed(1)} / {item.media_type}
                  </li>
                ))}
              </ul>
            </>
          ) : null}
        </div>
      </div>
    </section>
  )
}