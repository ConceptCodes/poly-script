import { expect, test } from "@playwright/test";

test.describe("Upload Flow E2E", () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to upload page
    await page.goto("/upload");
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

    // Create a test file
    const _testFile = {
      name: "test-audio.mp3",
      mimeType: "audio/mpeg",
      buffer: Buffer.from("test audio content"),
    };

    // Mock the API response
    await page.route("**/v1/jobs", async (route) => {
      await route.fulfill({
        status: 201,
        contentType: "application/json",
        body: JSON.stringify({ job_id: "test-job-123" }),
      });
    });

    // Upload file (this would require actual file input handling)
    // For now, just verify the flow structure
    await expect(page.getByText("Drag and drop audio file")).toBeVisible();
  });

  test("URL submission flow", async ({ page }) => {
    // Switch to URL tab
    await page.getByRole("tab", { name: "From URL" }).click();

    // Check URL input
    await expect(page.getByPlaceholder(/youtube/i)).toBeVisible();

    // Mock the API response
    await page.route("**/v1/jobs/url", async (route) => {
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
    // Mock API to return limit reached
    await page.route("**/v1/billing/usage", async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          monthly_upload_count: 10,
          monthly_limit: 10,
          extra_credits: 0,
          plan: "STANDARD",
        }),
      });
    });

    // Reload page to trigger mocked data
    await page.reload();

    // Check limit card appears
    await expect(page.getByText(/monthly limit reached/i)).toBeVisible();

    // Check upgrade button
    await expect(page.getByRole("button", { name: /upgrade/i })).toBeVisible();
  });
});
