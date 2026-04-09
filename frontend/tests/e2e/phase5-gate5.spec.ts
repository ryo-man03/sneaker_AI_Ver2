// file: tests/e2e/phase5-gate5.spec.ts
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

test('phase5 buyscore and dataops flow', async ({ page }) => {
  const errors = attachClientErrorMonitor(page)
  await login(page)

  await page.getByRole('button', { name: /BuyScore 調整/ }).click()
  await expect(page).toHaveURL(/\/buyscore/)
  await expect(page.getByRole('heading', { name: 'BuyScore 調整' })).toBeVisible()
  await expect(page.getByRole('heading', { name: '総合 BuyScore' })).toBeVisible()

  await page.getByRole('button', { name: '再計算' }).click()
  await expect(page.getByText('partial mode:')).toBeVisible()

  await page.getByRole('button', { name: /データ収集 \/ AI/ }).click()
  await expect(page).toHaveURL(/\/dataops/)
  await expect(page.getByRole('heading', { name: 'データ収集 / AI' })).toBeVisible()

  await page.getByLabel('Intake Type').selectOption('url')
  await page.getByLabel('Payload').fill('https://example.com/items/test')
  await page.getByRole('button', { name: '取り込み実行' }).click()
  await expect(page.getByText('accepted: true')).toBeVisible()
  await expect(page.getByRole('heading', { name: 'Correlation Summary' })).toBeVisible()

  assertNoClientErrors(errors)
})