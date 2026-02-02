import { test, expect } from '@playwright/test';

test.describe('Transcript Editor E2E', () => {
  test.beforeEach(async ({ page }) => {
    // Mock authentication
    await page.goto('/');
    await page.evaluate(() => {
      localStorage.setItem('access_token', 'mock-token');
      localStorage.setItem('user_id', 'mock-user-id');
    });
  });

  test('editor page loads with transcript data', async ({ page }) => {
    // Mock API responses
    await page.route('**/v1/transcripts/**', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          id: 'test-transcript-id',
          job_id: 'test-job-id',
          text: 'This is a test transcript with multiple segments.',
          language: 'en',
          segments: [
            {
              id: 0,
              start_ms: 0,
              end_ms: 3000,
              text: 'This is a test transcript',
              speaker: null,
            },
            {
              id: 1,
              start_ms: 3000,
              end_ms: 6000,
              text: 'with multiple segments.',
              speaker: null,
            },
          ],
          engine_version: 'test-engine-v1',
          created_at: new Date().toISOString(),
          updated_at: null,
        }),
      });
    });

    // Navigate to editor
    await page.goto('/transcripts/test-transcript-id');

    // Check page title
    await expect(page.getByRole('heading')).toContainText('Transcript');

    // Check segments are displayed
    await expect(page.locator('[data-segment-id="0"]')).toBeVisible();
    await expect(page.locator('[data-segment-id="1"]')).toBeVisible();

    // Check segment text
    await expect(page.locator('[data-segment-id="0"]')).toContainText('This is a test transcript');
  });

  test('can edit segment text', async ({ page }) => {
    // Mock API responses
    await page.route('**/v1/transcripts/**', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          id: 'test-id',
          job_id: 'test-job-id',
          text: 'Original text',
          language: 'en',
          segments: [{
            id: 0,
            start_ms: 0,
            end_ms: 3000,
            text: 'Original text',
            speaker: null,
          }],
          engine_version: 'test',
          created_at: new Date().toISOString(),
          updated_at: null,
        }),
      });
    });

    // Mock update API
    await page.route('**/v1/transcripts/**/segments/**', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          id: 0,
          start_ms: 0,
          end_ms: 3000,
          text: 'Updated text',
          speaker: null,
        }),
      });
    });

    await page.goto('/transcripts/test-id');

    // Click edit on first segment
    await page.locator('[data-segment-id="0"]').getByRole('button', { name: /edit/i }).click();

    // Wait for textarea to appear
    const textarea = page.locator('[data-segment-id="0"] textarea').first();
    await textarea.waitFor();

    // Update text
    await textarea.fill('Updated text');

    // Click save
    await page.getByRole('button', { name: /save/i }).click();

    // Wait for save to complete
    await expect(page.locator('[data-segment-id="0"]')).toContainText('Updated text');
  });

  test('can split a segment', async ({ page }) => {
    await page.route('**/v1/transcripts/**', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          id: 'test-id',
          job_id: 'test-job-id',
          text: 'Long segment that should be split',
          language: 'en',
          segments: [{
            id: 0,
            start_ms: 0,
            end_ms: 6000,
            text: 'Long segment that should be split',
            speaker: null,
          }],
          engine_version: 'test',
          created_at: new Date().toISOString(),
          updated_at: null,
        }),
      });
    });

    await page.goto('/transcripts/test-id');

    // Click split button
    await page.locator('[data-segment-id="0"]').getByRole('button', { name: /split/i }).click();

    // Wait for split dialog
    await expect(page.getByText('Split Segment')).toBeVisible();

    // Move slider to split at 3000ms
    const slider = page.locator('input[type="range"]');
    await slider.fill('3000');

    // Confirm split
    await page.getByRole('button', { name: /split/i }).click();

    // Wait for split to complete - 2 segments should be visible
    await expect(page.locator('[data-segment-id="0"]')).toBeVisible();
    await expect(page.locator('[data-segment-id="1"]')).toBeVisible();
  });

  test('can merge segments', async ({ page }) => {
    await page.route('**/v1/transcripts/**', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          id: 'test-id',
          job_id: 'test-job-id',
          text: 'First segment Second segment Third segment',
          language: 'en',
          segments: [
            { id: 0, start_ms: 0, end_ms: 2000, text: 'First segment', speaker: null },
            { id: 1, start_ms: 2000, end_ms: 4000, text: 'Second segment', speaker: null },
            { id: 2, start_ms: 4000, end_ms: 6000, text: 'Third segment', speaker: null },
          ],
          engine_version: 'test',
          created_at: new Date().toISOString(),
          updated_at: null,
        }),
      });
    });

    await page.goto('/transcripts/test-id');

    // Select first two segments for merge
    await page.locator('[data-segment-id="0"] input[type="checkbox"]').click();
    await page.locator('[data-segment-id="1"] input[type="checkbox"]').click();

    // Click merge button in floating bar
    await page.getByRole('button', { name: /merge/i }).click();

    // Wait for merge to complete - 2 segments should remain
    await expect(page.locator('[data-segment-id="0"]')).toBeVisible();
    await expect(page.locator('[data-segment-id="1"]')).not.toBeVisible();
    await expect(page.locator('[data-segment-id="2"]')).toBeVisible();
  });

  test('export modal works with async export', async ({ page }) => {
    await page.route('**/v1/transcripts/**', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          id: 'test-id',
          job_id: 'test-job-id',
          text: 'Test transcript',
          language: 'en',
          segments: [{ id: 0, start_ms: 0, end_ms: 3000, text: 'Test', speaker: null }],
          engine_version: 'test',
          created_at: new Date().toISOString(),
          updated_at: null,
        }),
      });
    });

    await page.goto('/transcripts/test-id');

    // Click export button
    await page.getByRole('button', { name: /export/i }).click();

    // Wait for export modal
    await expect(page.getByText('Export')).toBeVisible();

    // Check export formats are visible
    await expect(page.getByText('Plain Text (TXT)')).toBeVisible();
    await expect(page.getByText('SRT')).toBeVisible();
    await expect(page.getByText('VTT')).toBeVisible();
    await expect(page.getByText('JSON')).toBeVisible();
  });
});
