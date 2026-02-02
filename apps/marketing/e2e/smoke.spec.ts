import { test, expect } from '@playwright/test';

const locales = ['en', 'de', 'es', 'fr', 'jp'];
const routes = ['', '/features', '/pricing', '/docs', '/blog', '/legal', '/contact'];

test.describe('Marketing Site Smoke Tests', () => {
  locales.forEach(locale => {
    test.describe(`Locale: ${locale}`, () => {
      test.beforeEach(async ({ page }) => {
        await page.goto(`/${locale}`);
      });

      routes.forEach(route => {
        test(`Route /${locale}${route || '/'} loads successfully`, async ({ page }) => {
          const response = await page.goto(`/${locale}${route}`);
          expect(response?.status()).toBe(200);
        });

        test(`Route /${locale}${route || '/'} has correct title`, async ({ page }) => {
          await page.goto(`/${locale}${route}`);
          const title = await page.title();
          expect(title).toContain('PolyScript');
        });

        test(`Route /${locale}${route || '/'} has no console errors`, async ({ page }) => {
          const errors: string[] = [];
          page.on('console', msg => {
            if (msg.type() === 'error') {
              errors.push(msg.text());
            }
          });
          await page.goto(`/${locale}${route}`);
          await page.waitForLoadState('networkidle');
          expect(errors.length).toBe(0);
        });
      });

      test('Language switcher works', async ({ page }) => {
        await page.goto(`/${locale}`);
        const select = page.locator('.lang select');
        await expect(select).toBeVisible();
        await select.selectOption('en');
        await expect(page).toHaveURL('/en');
      });

      test('Navigation links work', async ({ page }) => {
        await page.goto(`/${locale}`);
        await page.click('a[href*="/features"]');
        await expect(page).toHaveURL(/\/features/);
        await page.click('a[href*="/pricing"]');
        await expect(page).toHaveURL(/\/pricing/);
        await page.click('a[href*="/docs"]');
        await expect(page).toHaveURL(/\/docs/);
        await page.click('a[href*="/blog"]');
        await expect(page).toHaveURL(/\/blog/);
        await page.click('a[href*="/contact"]');
        await expect(page).toHaveURL(/\/contact/);
      });
    });
  });

  test('Home page has hero section', async ({ page }) => {
    await page.goto('/en');
    await expect(page.locator('.hero')).toBeVisible();
    await expect(page.locator('.hero-title')).toBeVisible();
    await expect(page.locator('.hero-subtitle')).toBeVisible();
  });

  test('Blog index shows posts', async ({ page }) => {
    await page.goto('/en/blog');
    await expect(page.locator('.card')).toHaveCount(3);
  });

  test('Docs index shows documentation', async ({ page }) => {
    await page.goto('/en/docs');
    await expect(page.locator('.card').first()).toBeVisible();
  });

  test('Legal index shows legal pages', async ({ page }) => {
    await page.goto('/en/legal');
    await expect(page.locator('.card')).toHaveCount(2);
  });

  test('Pricing page shows plans', async ({ page }) => {
    await page.goto('/en/pricing');
    await expect(page.locator('.pricing .card')).toHaveCount(3);
  });

  test('Contact form is present', async ({ page }) => {
    await page.goto('/en/contact');
    await expect(page.locator('input[name="name"]')).toBeVisible();
    await expect(page.locator('input[name="email"]')).toBeVisible();
    await expect(page.locator('textarea[name="message"]')).toBeVisible();
  });

  test('Responsive design works on mobile', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto('/en');
    await expect(page.locator('.hero')).toBeVisible();
    await expect(page.locator('.nav-links')).not.toBeVisible();
  });
});
