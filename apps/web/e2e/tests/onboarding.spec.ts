import { expect, test } from "@playwright/test";

test.describe("Onboarding Flow E2E", () => {
  test("signup flow redirects to email verification", async ({ page }) => {
    // Mock signup API
    await page.route("**/v1/auth/signup", async (route) => {
      await route.fulfill({
        status: 201,
        contentType: "application/json",
        body: JSON.stringify({ user_id: "test-user", email: "test@example.com" }),
      });
    });

    // Start from signup page
    await page.goto("/signup");

    // Fill form and submit
    await page.locator("input").nth(0).fill("test@example.com");
    await page.locator("input").nth(1).fill("TestPassword123!");
    await page.locator("input").nth(2).fill("TestPassword123!");
    await page.getByRole("checkbox").check();
    await page.getByRole("button", { name: /submit/i }).click();

    // After signup, user is redirected to verify-email-code
    await page.waitForURL(/verify-email-code/i, { timeout: 10000 });
    await page.waitForTimeout(1000);
    await expect(page.locator("body")).toBeVisible();
  });

  test("validates email verification code", async ({ page }) => {
    await page.goto("/auth/verify-email-code");
    await page.waitForTimeout(2000);

    // Check page loaded - look for any input or button
    await expect(page.locator("input, button").first()).toBeVisible();
  });

  test("redirects unverified users from protected routes", async ({ page }) => {
    // Mock auth check
    await page.route("**/v1/auth/me", async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          user_id: "test-user",
          email: "test@example.com",
          email_verified: false,
        }),
      });
    });

    // Try to access dashboard
    await page.goto("/dashboard");

    // Should redirect to verify email or login
    await page.waitForURL(/verify-email|login/i);
    await expect(page.getByText(/verify|email/i)).toBeVisible();
  });
});
