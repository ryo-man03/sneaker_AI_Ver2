// file: src/pages/DashboardPage.tsx
import { SNEAKERS, formatYen } from '../data/sneakers'

type DashboardPageProps = {
  onOpenDetail: (sku: string) => void
}

const alerts = [
  { tone: 'red', message: '[Price Alert] AJ1 Bred が目標価格に到達' },
  { tone: 'amber', message: '[Trend Alert] NB 9060 BuyScore +18pt' },
  { tone: 'cyan', message: '[Release] Yeezy 350 "Onyx" 明日発売' },
  { tone: 'green', message: '[System] クローラー完了 2,841件更新' },
] as const

export function DashboardPage({ onOpenDetail }: DashboardPageProps) {
  return (
    <section className="page">
      <div className="section-header">
        <h2>ダッシュボード</h2>
        <span>リアルタイム市場概観 // LIVE</span>
      </div>
      <div className="kpi-grid">
        <article className="kpi-card cyan">
          <div>追跡スニーカー数</div>
          <strong>2,841</strong>
          <p className="kpi-change up">↑ +128 今週</p>
        </article>
        <article className="kpi-card green">
          <div>平均 BuyScore</div>
          <strong>73.2</strong>
          <p className="kpi-change up">↑ +2.4</p>
        </article>
        <article className="kpi-card amber">
          <div>ポートフォリオ総額</div>
          <strong>¥482K</strong>
          <p className="kpi-change up">↑ +8.3%</p>
        </article>
        <article className="kpi-card red">
          <div>価格アラート</div>
          <strong>3</strong>
          <p className="kpi-change down">要確認</p>
        </article>
      </div>
      <div className="panel-grid">
        <article className="panel">
          <h3>トレンド / 注目モデル</h3>
          <div className="sneaker-list">
            {SNEAKERS.slice(0, 4).map((shoe) => (
              <button
                key={shoe.sku}
                className="sneaker-row"
                type="button"
                onClick={() => onOpenDetail(shoe.sku)}
              >
                <span className="sneaker-thumb">👟</span>
                <span className="sneaker-info">
                  <span className="sneaker-name">{shoe.model}</span>
                  <span className="sneaker-meta">
                    {shoe.brand} // {shoe.sku}
                  </span>
                </span>
                <span className="sneaker-price">{formatYen(shoe.marketPrice)}</span>
                <span className="sneaker-score">{shoe.buyScore}</span>
              </button>
            ))}
          </div>
        </article>
        <article className="panel">
          <h3>最新アラート</h3>
          <ul className="list">
            {alerts.map((alert) => (
              <li key={alert.message} className={`alert-${alert.tone}`}>
                {alert.message}
              </li>
            ))}
          </ul>
        </article>
      </div>
    </section>
  )
}
