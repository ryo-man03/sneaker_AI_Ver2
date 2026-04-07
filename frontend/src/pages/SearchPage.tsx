// file: src/pages/SearchPage.tsx
type SearchPageProps = {
  onOpenDetail: () => void
}

export function SearchPage({ onOpenDetail }: SearchPageProps) {
  return (
    <section className="page">
      <div className="section-header">
        <h2>スニーカー検索</h2>
        <span>42サイト統合インデックス</span>
      </div>
      <div className="panel">
        <h3>検索結果</h3>
        <table className="data-table">
          <thead>
            <tr>
              <th>モデル名</th>
              <th>ブランド</th>
              <th>SKU</th>
              <th>市場価格</th>
              <th>BuyScore</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>Air Jordan 1 Retro High OG "Bred"</td>
              <td>NIKE</td>
              <td>555088-001</td>
              <td>¥48,500</td>
              <td>89</td>
              <td>
                <button className="btn-ghost" type="button" onClick={onOpenDetail}>
                  詳細
                </button>
              </td>
            </tr>
            <tr>
              <td>Yeezy Boost 350 V2 "Onyx"</td>
              <td>ADIDAS</td>
              <td>HQ4540</td>
              <td>¥32,000</td>
              <td>62</td>
              <td>
                <button className="btn-ghost" type="button" onClick={onOpenDetail}>
                  詳細
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>
  )
}
