import { test, expect } from '@playwright/test';

test('sample e2e test', async ({ page }) => {
  await page.goto('/');
  await expect(page).toHaveTitle(/PolyScript/);
});
