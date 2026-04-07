// file: src/pages/PlaceholderPage.tsx
type PlaceholderPageProps = {
  title: string
  subtitle: string
}

export function PlaceholderPage({ title, subtitle }: PlaceholderPageProps) {
  return (
    <section className="page">
      <div className="section-header">
        <h2>{title}</h2>
        <span>{subtitle}</span>
      </div>
      <div className="panel">
        <h3>Phase 1 Scaffold</h3>
        <p>このページは構造と遷移を先に確立し、Phase 2以降で機能を追加します。</p>
      </div>
    </section>
  )
}
