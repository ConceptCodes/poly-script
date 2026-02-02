import { test, expect } from '@playwright/test';

test.describe('Onboarding Flow E2E', () => {
  test('completes onboarding from start to finish', async ({ page }) => {
    // Mock signup API
    await page.route('**/v1/auth/signup', async (route) => {
      await route.fulfill({
        status: 201,
        contentType: 'application/json',
        body: JSON.stringify({ user_id: 'test-user', email: 'test@example.com' }),
      });
    });

    // Mock email verification
    await page.route('**/v1/auth/verify-email-code', async (route) => {
      await route.fulfill({ status: 204 });
    });

    // Mock onboarding completion
    await page.route('**/v1/onboarding/complete', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ team_id: 'test-team', plan: 'STANDARD' }),
      });
    });

    // Start from signup page
    await page.goto('/signup');

    // Complete signup
    await page.getByPlaceholder(/email/i).fill('test@example.com');
    await page.getByPlaceholder(/password/i).fill('TestPassword123!');
    await page.getByRole('button', { name: /sign up/i }).click();

    // Navigate to onboarding
    await page.waitForURL(/onboarding/i);

    // Language step
    await expect(page.getByText(/select language/i)).toBeVisible();
    await page.getByText(/english/i).click();
    await page.getByRole('button', { name: /continue/i }).click();

    // Team name step
    await expect(page.getByText(/create your team/i)).toBeVisible();
    await page.getByPlaceholder(/team name/i).fill('Test Team');
    await page.getByRole('button', { name: /continue/i }).click();

    // Plan selection step
    await expect(page.getByText(/choose your plan/i)).toBeVisible();
    await page.getByText(/standard/i).click();
    await page.getByRole('button', { name: /continue/i }).click();

    // Should navigate to dashboard
    await page.waitForURL(/dashboard/i);
    await expect(page.getByText(/welcome to test team/i)).toBeVisible();
  });

  test('validates email verification code', async ({ page }) => {
    await page.goto('/verify-email');

    await expect(page.getByPlaceholder(/verification code/i)).toBeVisible();
    await expect(page.getByRole('button', { name: /verify/i })).toBeVisible();
  });

  test('redirects unverified users from protected routes', async ({ page }) => {
    // Mock auth check
    await page.route('**/v1/auth/me', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ 
          user_id: 'test-user',
          email: 'test@example.com',
          email_verified: false,
        }),
      });
    });

    // Try to access dashboard
    await page.goto('/dashboard');

    // Should redirect to verify email
    await page.waitForURL(/verify-email/i);
    await expect(page.getByText(/verify your email/i)).toBeVisible();
  });
});
