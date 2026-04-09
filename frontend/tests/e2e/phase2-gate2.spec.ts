// file: tests/e2e/phase2-gate2.spec.ts
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

  page.on('requestfailed', (request: { method: () => string; url: () => string; failure: () => { errorText?: string } | null }) => {
    const failure = request.failure()
    const reason = failure?.errorText ?? ''
    if (reason.includes('ERR_ABORTED')) {
      return
    }
    errors.push(`requestfailed: ${request.method()} ${request.url()} ${reason}`.trim())
  })

  return errors
}

function assertNoClientErrors(errors: string[]) {
  expect.soft(errors, errors.join('\n')).toEqual([])
}

test('login to dashboard and basic layout visible', async ({ page }) => {
  const errors = attachClientErrorMonitor(page)
  await page.goto('/login')

  await page.getByLabel('メールアドレス').fill('yamada@example.com')
  await page.getByLabel('パスワード').fill('password123')
  await page.getByRole('button', { name: /ログイン/ }).click()

  await expect(page).toHaveURL(/\/dashboard/)
  await expect(page.getByRole('heading', { name: 'ダッシュボード' })).toBeVisible()
  await expect(page.getByText('SOLE//MATRIX /')).toBeVisible()
  assertNoClientErrors(errors)
})

test('sidebar search to detail and refresh restore', async ({ page }) => {
  const errors = attachClientErrorMonitor(page)
  await page.goto('/login')

  await page.getByLabel('メールアドレス').fill('yamada@example.com')
  await page.getByLabel('パスワード').fill('password123')
  await page.getByRole('button', { name: /ログイン/ }).click()

  await page.getByRole('button', { name: /スニーカー検索/ }).click()
  await expect(page).toHaveURL(/\/search/)

  await page.getByRole('button', { name: '詳細' }).first().click()
  await expect(page).toHaveURL(/\/detail/)
  await expect(page.getByRole('heading', { name: 'スニーカー詳細' })).toBeVisible()

  await page.reload()
  await expect(page).toHaveURL(/\/detail/)
  await expect(page.getByRole('heading', { name: 'スニーカー詳細' })).toBeVisible()
  assertNoClientErrors(errors)
})

test('sidebar market and stocks pages render', async ({ page }) => {
  const errors = attachClientErrorMonitor(page)
  await page.goto('/login')

  await page.getByLabel('メールアドレス').fill('yamada@example.com')
  await page.getByLabel('パスワード').fill('password123')
  await page.getByRole('button', { name: /ログイン/ }).click()

  await page.getByRole('button', { name: /市場価格/ }).click()
  await expect(page).toHaveURL(/\/market/)
  await expect(page.getByRole('heading', { name: '市場価格 / 相場' })).toBeVisible()

  await page.getByRole('button', { name: /株価監視/ }).click()
  await expect(page).toHaveURL(/\/stocks/)
  await expect(page.getByRole('heading', { name: '株価監視' })).toBeVisible()
  assertNoClientErrors(errors)
})
