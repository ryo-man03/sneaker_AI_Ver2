// file: tests/e2e/phase6-gate6.spec.ts
import { expect, test, type Page } from '@playwright/test'

function attachClientErrorMonitor(page: Page) {
  const errors: string[] = []

  page.on('pageerror', (error: Error) => {
    errors.push(`pageerror: ${error.message}`)
  })

  page.on('console', (message: { type: () => string; text: () => string }) => {
    if (message.type() === 'error') {
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

test('phase6 notification center dispatch and dedupe flow', async ({ page }) => {
  const errors = attachClientErrorMonitor(page)

  await login(page)

  await page.goto('/wishlist')
  await expect(page).toHaveURL(/\/wishlist/)

  await page.getByLabel('SKU').nth(1).fill('555088-001')
  await page.getByLabel('Threshold').fill('50000')
  await page.getByLabel('Cooldown(min)').fill('1')
  await page.getByRole('button', { name: 'ルール保存' }).click()

  await page.getByRole('button', { name: /通知センター/ }).click()
  await expect(page).toHaveURL(/\/notifications/)
  await expect(page.getByRole('heading', { name: '通知センター' })).toBeVisible()

  await page.getByRole('button', { name: '今すぐ評価実行' }).click()
  await expect(page.getByText('status: ok')).toBeVisible()
  await expect(page.getByText('triggered:')).toBeVisible()

  await page.getByRole('button', { name: '今すぐ評価実行' }).click()
  await expect(page.getByText('duplicates:')).toBeVisible()

  assertNoClientErrors(errors)
})
