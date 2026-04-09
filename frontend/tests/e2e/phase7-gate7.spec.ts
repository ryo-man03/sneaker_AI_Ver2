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

async function mockAdminOps(page: Page) {
  let count = 0
  await page.route('**/api/v1/admin-ops/reliability', async (route: Route) => {
    count += 1
    if (count >= 2) {
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
          db_counts: {
            sneakers: 3,
            market_snapshots: 3,
            stock_snapshots: 3,
            wishlist_items: 1,
            closet_items: 1,
            price_alert_rules: 1,
            notification_events: 0,
          },
          scheduler: {
            running: true,
            interval_seconds: 60,
          },
          integrations: {
            gemini_configured: true,
            instagram_configured: true,
          },
          maintenance: {
            key_rotation_days: 90,
            dependency_audit_days: 30,
            release_channel: 'stable',
          },
          dqm: {
            passed: true,
            stale_count: 0,
            checks: [
              {
                key: 'core_data_seeded',
                ok: true,
                detail: 'sneakers=3',
              },
            ],
          },
        },
        source: 'admin-ops',
        updated_at: new Date().toISOString(),
        ai_available: false,
        partial: false,
      }),
    })
  })
}

test('phase7 gate7 admin ops reliability and graceful failure flow', async ({ page }) => {
  const errors = attachClientErrorMonitor(page)
  await mockAdminOps(page)
  await login(page)

  await page.goto('/admin')
  await expect(page.getByRole('heading', { name: '管理コンソール' })).toBeVisible()
  await expect(page.getByText('passed: true / stale_count: 0')).toBeVisible()
  await expect(page.getByText('gemini_configured: true')).toBeVisible()
  await expect(page.getByText('release_channel: stable')).toBeVisible()

  await page.getByRole('button', { name: '再取得' }).click()
  await expect(page.getByText('AdminOps reliability API の取得に失敗しました。')).toBeVisible()
  await expect(page.getByText('source: admin-ops')).toBeVisible()

  assertNoClientErrors(errors)
})
