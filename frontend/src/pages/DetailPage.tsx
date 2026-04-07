// file: src/pages/DetailPage.tsx
export function DetailPage() {
  const bars = [
    ['文化的希少性', 94],
    ['市場流動性', 88],
    ['価格モメンタム', 85],
    ['SNSトレンド', 91],
    ['ブランド指数', 96],
  ]

  return (
    <section className="page">
      <div className="section-header">
        <h2>スニーカー詳細</h2>
        <span>CultureVector + BuyScore 分析</span>
      </div>
      <div className="panel">
        <h3>Air Jordan 1 Retro High OG "Bred"</h3>
        <div className="detail-stats">
          <div>市場価格: ¥48,500</div>
          <div>定価: ¥16,500</div>
          <div>プレミアム率: +193%</div>
          <div>BuyScore: 89</div>
        </div>
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
      </div>
    </section>
  )
}
