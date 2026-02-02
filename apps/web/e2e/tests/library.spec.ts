import { test, expect } from '@playwright/test';

test.describe('Library Page E2E', () => {
  test.beforeEach(async ({ page }) => {
    // Mock authentication
    await page.goto('/');
    await page.evaluate(() => {
      localStorage.setItem('access_token', 'mock-token');
      localStorage.setItem('user_id', 'mock-user-id');
    });
  });

  test('library page loads with transcript list', async ({ page }) => {
    // Mock API responses
    await page.route('**/v1/transcripts**', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          transcripts: [
            {
              id: 'transcript-1',
              job_id: 'job-1',
              job_filename: 'audio1.mp3',
              text_preview: 'First transcript preview text...',
              language: 'en',
              created_at: new Date().toISOString(),
              updated_at: null,
            },
            {
              id: 'transcript-2',
              job_id: 'job-2',
              job_filename: 'audio2.mp3',
              text_preview: 'Second transcript preview text...',
              language: 'de',
              created_at: new Date(Date.now() - 86400000).toISOString(),
              updated_at: null,
            },
          ],
          total: 2,
          page: 1,
          page_size: 20,
        }),
      });
    });

    await page.goto('/library');

    // Check page title
    await expect(page.getByRole('heading', { name: 'Transcript Library' })).toBeVisible();

    // Check transcripts are displayed
    await expect(page.getByText('audio1.mp3')).toBeVisible();
    await expect(page.getByText('audio2.mp3')).toBeVisible();

    // Check language badges
    await expect(page.getByText('EN')).toBeVisible();
    await expect(page.getByText('DE')).toBeVisible();
  });

  test('search filters transcripts', async ({ page }) => {
    await page.route('**/v1/transcripts**', async (route) => {
      const url = new URL(route.request().url());
      const search = url.searchParams.get('search');
      
      // Return filtered results based on search
      const transcripts = [
        {
          id: 'transcript-1',
          job_id: 'job-1',
          job_filename: 'meeting.mp3',
          text_preview: 'Meeting transcript about project planning',
          language: 'en',
          created_at: new Date().toISOString(),
          updated_at: null,
        },
        {
          id: 'transcript-2',
          job_id: 'job-2',
          job_filename: 'call.mp3',
          text_preview: 'Phone call with client',
          language: 'en',
          created_at: new Date().toISOString(),
          updated_at: null,
        },
      ];
      
      let filtered = transcripts;
      if (search) {
        filtered = transcripts.filter(t => t.text_preview.toLowerCase().includes(search.toLowerCase()));
      }
      
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          transcripts: filtered,
          total: filtered.length,
          page: 1,
          page_size: 20,
        }),
      });
    });

    await page.goto('/library');

    // Enter search term
    await page.getByPlaceholder('Search transcripts...').fill('meeting');

    // Wait for filtered results
    await expect(page.getByText('meeting.mp3')).toBeVisible();
    await expect(page.getByText('call.mp3')).not.toBeVisible();

    // Clear search
    await page.getByPlaceholder('Search transcripts...').fill('');
    await expect(page.getByText('call.mp3')).toBeVisible();
  });

  test('language filter works', async ({ page }) => {
    await page.route('**/v1/transcripts**', async (route) => {
      const url = new URL(route.request().url());
      const language = url.searchParams.get('language');
      
      // Return filtered results based on language
      const transcripts = [
        {
          id: 'transcript-1',
          job_id: 'job-1',
          job_filename: 'english.mp3',
          text_preview: 'English transcript',
          language: 'en',
          created_at: new Date().toISOString(),
          updated_at: null,
        },
        {
          id: 'transcript-2',
          job_id: 'job-2',
          job_filename: 'german.mp3',
          text_preview: 'German transcript',
          language: 'de',
          created_at: new Date().toISOString(),
          updated_at: null,
        },
      ];
      
      let filtered = transcripts;
      if (language) {
        filtered = transcripts.filter(t => t.language === language);
      }
      
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          transcripts: filtered,
          total: filtered.length,
          page: 1,
          page_size: 20,
        }),
      });
    });

    await page.goto('/library');

    // Select German filter
    await page.getByRole('combobox').click();
    await page.getByText('German').click();

    // Verify German transcript is visible, English is not
    await expect(page.getByText('german.mp3')).toBeVisible();
    await expect(page.getByText('english.mp3')).not.toBeVisible();
  });

  test('sort by different options', async ({ page }) => {
    await page.route('**/v1/transcripts**', async (route) => {
      const url = new URL(route.request().url());
      const sort = url.searchParams.get('sort');
      
      // Return sorted results
      const transcripts = [
        {
          id: 'transcript-1',
          job_id: 'job-1',
          job_filename: 'old.mp3',
          text_preview: 'Old transcript',
          language: 'en',
          created_at: new Date(Date.now() - 172800000).toISOString(), // 2 days ago
          updated_at: new Date(Date.now() - 86400000).toISOString(),
        },
        {
          id: 'transcript-2',
          job_id: 'job-2',
          job_filename: 'new.mp3',
          text_preview: 'New transcript',
          language: 'en',
          created_at: new Date().toISOString(), // Today
          updated_at: new Date().toISOString(),
        },
      ];
      
      let sorted = [...transcripts];
      if (sort === 'created_at:desc') {
        sorted = transcripts.sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime());
      } else if (sort === 'created_at:asc') {
        sorted = transcripts.sort((a, b) => new Date(a.created_at).getTime() - new Date(b.created_at).getTime());
      } else if (sort === 'updated_at:desc') {
        sorted = transcripts.sort((a, b) => new Date(b.updated_at!).getTime() - new Date(a.updated_at!).getTime());
      }
      
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          transcripts: sorted,
          total: sorted.length,
          page: 1,
          page_size: 20,
        }),
      });
    });

    await page.goto('/library');

    // Default sort - newest first
    await expect(page.getByText('new.mp3')).toBeVisible();
    await expect(page.getByText('old.mp3')).toBeVisible();
  });

  test('can select and export multiple transcripts', async ({ page }) => {
    await page.route('**/v1/transcripts**', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          transcripts: [
            {
              id: 'transcript-1',
              job_id: 'job-1',
              job_filename: 'file1.mp3',
              text_preview: 'First transcript',
              language: 'en',
              created_at: new Date().toISOString(),
              updated_at: null,
            },
            {
              id: 'transcript-2',
              job_id: 'job-2',
              job_filename: 'file2.mp3',
              text_preview: 'Second transcript',
              language: 'en',
              created_at: new Date().toISOString(),
              updated_at: null,
            },
          ],
          total: 2,
          page: 1,
          page_size: 20,
        }),
      });
    });

    await page.goto('/library');

    // Select first transcript
    await page.locator('input[type="checkbox"]').first().click();
    await expect(page.getByText('1 selected')).toBeVisible();

    // Select second transcript
    await page.locator('input[type="checkbox"]').nth(1).click();
    await expect(page.getByText('2 selected')).toBeVisible();

    // Click export selected button
    await page.getByRole('button', { name: /export selected/i }).click();

    // Verify bulk export modal opens
    await expect(page.getByText('Bulk Export')).toBeVisible();
    await expect(page.getByText('Export 2 transcripts')).toBeVisible();
  });

  test('grid and list view toggle works', async ({ page }) => {
    await page.route('**/v1/transcripts**', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          transcripts: [{
            id: 'transcript-1',
            job_id: 'job-1',
            job_filename: 'test.mp3',
            text_preview: 'Test transcript',
            language: 'en',
            created_at: new Date().toISOString(),
            updated_at: null,
          }],
          total: 1,
          page: 1,
          page_size: 20,
        }),
      });
    });

    await page.goto('/library');

    // Default is grid view
    const gridIcon = page.locator('[data-testid="view-toggle"]').getByRole('button').first();
    const listIcon = page.locator('[data-testid="view-toggle"]').getByRole('button').nth(1);

    // Switch to list view
    await listIcon.click();
    // Verify list view is active (button has bg-muted class)
    await expect(listIcon).toHaveClass(/bg-muted/);

    // Switch back to grid view
    await gridIcon.click();
    await expect(gridIcon).toHaveClass(/bg-muted/);
  });

  test('pagination works', async ({ page }) => {
    // Mock API with pagination
    await page.route('**/v1/transcripts**', async (route) => {
      const url = new URL(route.request().url());
      const pageNum = parseInt(url.searchParams.get('page') || '1', 10);
      
      const allTranscripts = Array.from({ length: 25 }, (_, i) => ({
        id: `transcript-${i}`,
        job_id: `job-${i}`,
        job_filename: `file${i}.mp3`,
        text_preview: `Transcript ${i}`,
        language: 'en',
        created_at: new Date().toISOString(),
        updated_at: null,
      }));
      
      const pageTranscripts = allTranscripts.slice((pageNum - 1) * 20, pageNum * 20);
      
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          transcripts: pageTranscripts,
          total: 25,
          page: pageNum,
          page_size: 20,
        }),
      });
    });

    await page.goto('/library');

    // First page
    await expect(page.getByText('Page 1 of 2')).toBeVisible();
    await expect(page.getByText('file19.mp3')).toBeVisible();

    // Click next
    await page.getByRole('button', { name: /next/i }).click();

    // Second page
    await expect(page.getByText('Page 2 of 2')).toBeVisible();
    await expect(page.getByText('file20.mp3')).toBeVisible();
    await expect(page.getByText('file19.mp3')).not.toBeVisible();

    // Click previous
    await page.getByRole('button', { name: /previous/i }).click();

    // Back to first page
    await expect(page.getByText('Page 1 of 2')).toBeVisible();
  });
});
