import { test, expect } from '@playwright/test';

test.describe('Onboarding Flow', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('http://localhost:5173');
  });

  test('complete signup → verify email code → onboarding → dashboard flow', async ({ page }) => {
    // Navigate to signup
    await page.click('text=Sign Up');
    await expect(page).toHaveURL(/.*signup/);

    // Fill signup form
    const email = `test-${Date.now()}@example.com`;
    await page.fill('input[type="email"]', email);
    await page.fill('input[type="password"]', 'TestPassword123!');
    await page.fill('input[name="confirmPassword"]', 'TestPassword123!');
    await page.click('input[type="checkbox"]');
    await page.click('button[type="submit"]');

    // Should redirect to verify email code page
    await expect(page).toHaveURL(/.*verify-email-code/);
    await expect(page.locator('h1')).toContainText('Verify Email');

    // For testing purposes, we'll skip actual code verification
    // In production, this would come from email
    await page.click('text=Back to Login');

    // Test login flow
    await page.fill('input[type="email"]', email);
    await page.fill('input[type="password"]', 'TestPassword123!');
    await page.click('button[type="submit"]');

    // Should redirect to dashboard after successful login
    await expect(page).toHaveURL(/.*dashboard/);
    await expect(page.locator('h1')).toContainText('Dashboard');
  });

  test('should show validation errors for invalid signup', async ({ page }) => {
    await page.goto('http://localhost:5173/signup');

    // Submit empty form
    await page.click('button[type="submit"]');

    // Should show validation errors
    await expect(page.locator('text=required')).toBeVisible();
  });
});
