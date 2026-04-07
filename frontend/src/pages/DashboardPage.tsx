// file: src/pages/DashboardPage.tsx
export function DashboardPage() {
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
        </article>
        <article className="kpi-card green">
          <div>平均 BuyScore</div>
          <strong>73.2</strong>
        </article>
        <article className="kpi-card amber">
          <div>ポートフォリオ総額</div>
          <strong>¥482K</strong>
        </article>
        <article className="kpi-card red">
          <div>価格アラート</div>
          <strong>3</strong>
        </article>
      </div>
      <div className="panel-grid">
        <article className="panel">
          <h3>トレンド / 注目モデル</h3>
          <ul className="list">
            <li>Nike Air Jordan 1 Retro High OG / ¥48,500 / Score 89</li>
            <li>Adidas Yeezy Boost 350 V2 / ¥32,000 / Score 62</li>
            <li>New Balance 9060 / ¥21,000 / Score 77</li>
            <li>Nike Dunk Low Retro / ¥22,800 / Score 81</li>
          </ul>
        </article>
        <article className="panel">
          <h3>最新アラート</h3>
          <ul className="list">
            <li>[Price Alert] AJ1 Bred が目標価格に到達</li>
            <li>[Trend Alert] NB 9060 BuyScore +18pt</li>
            <li>[Release] Yeezy 350 "Onyx" 明日発売</li>
            <li>[System] クローラー完了 2,841件更新</li>
          </ul>
        </article>
      </div>
    </section>
  )
}
