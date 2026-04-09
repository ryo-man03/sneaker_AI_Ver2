// file: tests/e2e/phase4-gate4.spec.ts
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

test('phase4 wishlist closet portfolio flow', async ({ page }) => {
  const errors = attachClientErrorMonitor(page)
  const suffix = Date.now().toString().slice(-6)
  const wishlistSku = `WL-${suffix}`
  const closetSku = `CL-${suffix}`

  await login(page)

  await page.getByRole('button', { name: /ウィッシュリスト/ }).click()
  await expect(page).toHaveURL(/\/wishlist/)

  await page.getByLabel('SKU').first().fill(wishlistSku)
  await page.getByLabel('Model').fill('Wishlist Test Model')
  await page.getByLabel('Brand').fill('TEST')
  await page.getByLabel('Target Price').fill('21000')
  await page.getByLabel('Current Price').fill('24000')
  await page.getByLabel('Note').fill('gate4 e2e')
  await page.getByRole('button', { name: '追加' }).click()

  await expect(page.getByText(wishlistSku).first()).toBeVisible()

  await page.getByLabel('SKU').nth(1).fill(wishlistSku)
  await page.getByLabel('Threshold').fill('20000')
  await page.getByLabel('Cooldown(min)').fill('120')
  await page.getByRole('button', { name: 'ルール保存' }).click()

  await expect(page.getByText('price_below').first()).toBeVisible()

  await page.goto('/closet')
  await expect(page).toHaveURL(/\/closet/)

  await page.getByLabel('SKU').fill(closetSku)
  await page.getByLabel('Model').fill('Closet Test Model')
  await page.getByLabel('Brand').fill('TEST')
  await page.getByLabel('Quantity').fill('2')
  await page.getByLabel('Avg Buy Price').fill('18000')
  await page.getByLabel('Current Price').fill('21000')
  await page.getByRole('button', { name: '追加' }).click()

  await expect(page.getByText(closetSku).first()).toBeVisible()

  await page.goto('/portfolio')
  await expect(page).toHaveURL(/\/portfolio/)
  await expect(page.getByRole('heading', { name: 'Portfolio' })).toBeVisible()
  await expect(page.getByText('Holdings')).toBeVisible()

  assertNoClientErrors(errors)
})
