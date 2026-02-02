import { test, expect } from '@playwright/test';

test.describe('Settings Pages', () => {
  test('should load user settings page', async ({ page }) => {
    // This test would require authentication
    // For now, just test the page structure
    await page.goto('http://localhost:5173/settings/user');
    
    // Should redirect to login if not authenticated
    await expect(page).toHaveURL(/.*login/);
  });

  test('should load team settings page', async ({ page }) => {
    await page.goto('http://localhost:5173/settings/team');
    
    // Should redirect to login if not authenticated
    await expect(page).toHaveURL(/.*login/);
  });
});
