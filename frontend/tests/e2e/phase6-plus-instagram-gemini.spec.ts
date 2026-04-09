// file: tests/e2e/phase6-plus-instagram-gemini.spec.ts
import { expect, test, type Page, type Route } from '@playwright/test'

function attachClientErrorMonitor(page: Page) {
  const errors: string[] = []

  page.on('pageerror', (error: Error) => {
    errors.push(`pageerror: ${error.message}`)
  })

  page.on('console', (message: { type: () => string; text: () => string }) => {
    if (message.type() === 'error') {
      if (message.text().includes('500 (Internal Server Error)')) {
        return
      }
      errors.push(`console.error: ${message.text()}`)
    }
  })

  page.on(
    'requestfailed',
    (request: { method: () => string; url: () => string; failure: () => { errorText?: string } | null }) => {
      const failure = request.failure()
      const reason = failure?.errorText ?? ''
      if (reason.includes('ERR_ABORTED')) {
        return
      }
      errors.push(`requestfailed: ${request.method()} ${request.url()} ${reason}`.trim())
    },
  )

  return errors
}

function assertNoClientErrors(errors: string[]) {
  expect.soft(errors, errors.join('\n')).toEqual([])
}

async function login(page: Page) {
  await page.goto('/login')
  await page.getByLabel('メールアドレス').fill('yamada@example.com')
  await page.getByLabel('パスワード').fill('password123')
  await page.getByRole('button', { name: /ログイン/ }).click()
  await expect(page).toHaveURL(/\/dashboard/)
}

async function mockAiEndpoints(page: Page) {
  await page.route('**/api/v1/search-grounding/answer', async (route: Route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        data: {
          query: 'mock query',
          answer: 'mock grounded answer',
          citations: [
            {
              title: 'source-1',
              url: 'https://example.com/source',
              snippet: 'mock snippet',
            },
          ],
        },
        source: 'grounded-search:gemini-2.5-flash',
        updated_at: new Date().toISOString(),
        ai_available: true,
        partial: false,
      }),
    })
  })

  await page.route('**/api/v1/image-analysis/analyze', async (route: Route) => {
    const body = route.request().postDataJSON() as { image_url?: string }
    if ((body.image_url ?? '').includes('fail')) {
      await route.fulfill({
        status: 500,
        contentType: 'application/json',
        body: JSON.stringify({ detail: 'mock failure' }),
      })
      return
    }

    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        data: {
          is_sneaker: true,
          brand: 'NIKE',
          model: 'Jordan 1',
          colorway: 'Bred',
          material: 'Leather',
          notes: ['mock-note'],
          confidence: 0.91,
        },
        source: 'gemini:gemini-2.5-flash',
        updated_at: new Date().toISOString(),
        ai_available: true,
        partial: false,
      }),
    })
  })

  await page.route('**/api/v1/instagram/trends**', async (route: Route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        data: {
          query: 'sneakers',
          total: 1,
          items: [
            {
              hashtag: '#sneakers',
              caption: 'mock trend',
              media_type: 'IMAGE',
              permalink: 'https://instagram.com/p/mock',
              engagement_score: 132,
              observed_at: new Date().toISOString(),
            },
          ],
        },
        source: 'instagram',
        updated_at: new Date().toISOString(),
        ai_available: true,
        partial: false,
      }),
    })
  })
}

test('phase6+ grounded search image analysis and instagram trend UI flow', async ({ page }) => {
  const errors = attachClientErrorMonitor(page)
  await mockAiEndpoints(page)
  await login(page)

  await page.goto('/search')
  await page.getByRole('button', { name: '検索補助AI回答' }).click()
  await expect(page.getByRole('heading', { name: '検索補助AI回答' })).toBeVisible()
  await expect(page.getByText('mock grounded answer')).toBeVisible()

  await page.goto('/detail')
  await page.getByRole('button', { name: '画像解析を実行' }).click()
  await expect(page.getByText('sneaker: true')).toBeVisible()

  await page.getByLabel('Image URL').fill('https://example.com/fail.jpg')
  await page.getByRole('button', { name: '画像解析を実行' }).click()
  await expect(page.getByText('画像解析APIの実行に失敗しました。')).toBeVisible()

  await page.goto('/dataops')
  await page.getByRole('button', { name: '取得', exact: true }).click()
  await expect(page.getByRole('heading', { name: 'Instagram Trend Source' })).toBeVisible()
  await expect(page.getByText('source: instagram')).toBeVisible()

  assertNoClientErrors(errors)
})
