import { expect, test } from "@playwright/test";

test.describe("Upload Flow E2E", () => {
  test.beforeEach(async ({ page }) => {
    // Set up global error logging
    page.on("console", (msg) => {
      if (msg.type() === "error") {
        console.log(`Console error: ${msg.text()}`);
      }
    });

    page.on("pageerror", (err) => {
      console.log(`Page error: ${err.message}`);
    });

    // Navigate to login first to establish origin, then set auth state
    await page.goto("/login");
    await page.waitForTimeout(100);

    // Set auth state in localStorage after page load
    await page.evaluate(() => {
      localStorage.setItem("access_token", "mock-token");
      localStorage.setItem("user_id", "mock-user-id");
    });

    // Mock auth/me endpoint for proper auth hydration
    await page.route("**/v1/auth/me**", async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          user: {
            id: "mock-user-id",
            email: "test@example.com",
            name: "Test User",
            verified: true,
            createdAt: new Date().toISOString(),
            host_language: "en",
            theme: "system",
            notifications: {
              email: true,
              job_completion: true,
              in_app: true,
            },
          },
          team: {
            id: "team-1",
            name: "Test Team",
            defaultLanguage: "en",
            createdAt: new Date().toISOString(),
          },
        }),
      });
    });

    // Mock billing/usage API (no /v1 prefix - matches useUsage hook)
    await page.route("**/billing/usage**", async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          plan: "STANDARD",
          monthly_upload_count: 5,
          monthly_limit: 25,
          extra_credits: 0,
        }),
      });
    });

    // Mock billing/pricing API (no /v1 prefix - matches usePricing hook)
    await page.route("**/billing/pricing**", async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          credit_price: 100,
          plans: [
            {
              plan: "FREE",
              limits: { uploads_per_month: 5, languages: 2, members: 1 },
            },
            {
              plan: "STANDARD",
              limits: { uploads_per_month: 25, languages: 5, members: 5 },
            },
            {
              plan: "PRO",
              limits: { uploads_per_month: -1, languages: 5, members: -1 },
            },
          ],
        }),
      });
    });

    // Mock team settings API (has /v1 prefix - matches useTeamSettings hook)
    await page.route("**/v1/settings/team**", async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          id: "team-1",
          name: "Test Team",
          default_language: "en",
          plan: "STANDARD",
          credits_balance: 0,
          members_count: 1,
          created_at: new Date().toISOString(),
        }),
      });
    });

    // Wait for auth to initialize
    await page.waitForTimeout(500);

    // Navigate to upload page
    await page.goto("/upload");
    await page.waitForTimeout(500);
  });

  test("upload page loads with correct elements", async ({ page }) => {
    // Check title
    await expect(page.getByRole("heading", { name: "Upload Audio" })).toBeVisible();

    // Check tabs
    await expect(page.getByRole("tab", { name: "Upload File" })).toBeVisible();
    await expect(page.getByRole("tab", { name: "From URL" })).toBeVisible();

    // Check upload options form
    await expect(page.getByRole("combobox", { name: /language/i })).toBeVisible();
  });

  test("file upload flow", async ({ page }) => {
    // Click file upload tab
    await page.getByRole("tab", { name: "Upload File" }).click();

    // Mock the API response for job creation
    await page.route("**/v1/jobs**", async (route) => {
      await route.fulfill({
        status: 201,
        contentType: "application/json",
        body: JSON.stringify({ job_id: "test-job-123" }),
      });
    });

    // Verify dropzone is visible with correct text
    await expect(page.getByText("Drop audio file here or click to browse")).toBeVisible();
    await expect(page.getByText("Supports MP3, WAV, M4A, OGG, WEBM")).toBeVisible();
  });

  test("URL submission flow", async ({ page }) => {
    // Switch to URL tab
    await page.getByRole("tab", { name: "From URL" }).click();

    // Check URL input
    await expect(page.getByPlaceholder(/youtube/i)).toBeVisible();

    // Mock the API response for URL job creation
    await page.route("**/v1/jobs/url**", async (route) => {
      await route.fulfill({
        status: 201,
        contentType: "application/json",
        body: JSON.stringify({ job_id: "test-job-456" }),
      });
    });

    // Enter YouTube URL
    await page.getByPlaceholder(/youtube/i).fill("https://youtube.com/watch?v=test123");

    // Verify no error
    await expect(page.getByText(/invalid url/i)).not.toBeVisible();
  });

  test("URL validation shows error for invalid URLs", async ({ page }) => {
    // Switch to URL tab
    await page.getByRole("tab", { name: "From URL" }).click();

    // Enter invalid URL
    await page.getByPlaceholder(/youtube/i).fill("not-a-url");

    // Check error message
    await expect(page.getByText(/invalid url/i)).toBeVisible();
  });

  test("upgrade CTA appears when plan limit reached", async ({ page }) => {
    // Override the default billing mock to return limit reached
    await page.route("**/billing/usage**", async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          plan: "FREE",
          monthly_upload_count: 5,
          monthly_limit: 5,
          extra_credits: 0,
        }),
      });
    });

    // Override pricing mock for FREE plan limits
    await page.route("**/billing/pricing**", async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          credit_price: 100,
          plans: [
            {
              plan: "FREE",
              limits: { uploads_per_month: 5, languages: 2, members: 1 },
            },
            {
              plan: "STANDARD",
              limits: { uploads_per_month: 25, languages: 5, members: 5 },
            },
            {
              plan: "PRO",
              limits: { uploads_per_month: -1, languages: 5, members: -1 },
            },
          ],
        }),
      });
    });

    // Reload page to trigger mocked data
    await page.reload();
    await page.waitForTimeout(1000);

    // Check limit card appears (exact title from PlanLimitCard)
    await expect(page.getByText("Upload Limit Reached")).toBeVisible();

    // Check upgrade button (use first() in case there are multiple upgrade buttons on page)
    await expect(page.getByRole("button", { name: /upgrade/i }).first()).toBeVisible();
  });
});
