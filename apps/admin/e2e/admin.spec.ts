import { test, expect } from "@playwright/test";

const ADMIN_URL = process.env.ADMIN_URL || "http://localhost:5174";

test.describe("Admin Authentication", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto(`${ADMIN_URL}/login`);
  });

  test("displays login form", async ({ page }) => {
    await expect(page.locator("text=Admin Login")).toBeVisible();
    await expect(page.locator('input[type="email"]')).toBeVisible();
    await expect(page.locator('input[type="password"]')).toBeVisible();
    await expect(page.locator('button:has-text("Login")')).toBeVisible();
  });

  test("shows error for invalid credentials", async ({ page }) => {
    await page.fill('input[type="email"]', "invalid@test.com");
    await page.fill('input[type="password"]', "wrongpassword");
    await page.click('button:has-text("Login")');

    await expect(page.locator("text=Invalid credentials")).toBeVisible();
  });
});

test.describe("Admin Dashboard", () => {
  test.beforeEach(async ({ page }) => {
    // Login as admin
    await page.goto(`${ADMIN_URL}/login`);
    await page.fill('input[type="email"]', "admin@test.com");
    await page.fill('input[type="password"]', "correctpassword");
    await page.click('button:has-text("Login")');
    await page.waitForURL(`${ADMIN_URL}/`);
  });

  test("displays dashboard stats", async ({ page }) => {
    await expect(page.locator("text=Total Users")).toBeVisible();
    await expect(page.locator("text=Total Teams")).toBeVisible();
    await expect(page.locator("text=Total Jobs")).toBeVisible();
  });

  test("displays system health", async ({ page }) => {
    await expect(page.locator("text=API Status")).toBeVisible();
    await expect(page.locator("text=Queue Depth")).toBeVisible();
    await expect(page.locator("text=Worker Status")).toBeVisible();
  });
});

test.describe("Admin Users Management", () => {
  test.beforeEach(async ({ page }) => {
    // Login as admin
    await page.goto(`${ADMIN_URL}/login`);
    await page.fill('input[type="email"]', "admin@test.com");
    await page.fill('input[type="password"]', "correctpassword");
    await page.click('button:has-text("Login")');
    await page.waitForURL(`${ADMIN_URL}/`);

    // Navigate to users
    await page.click('a:has-text("Users")');
    await page.waitForURL(`${ADMIN_URL}/users`);
  });

  test("displays users list", async ({ page }) => {
    await expect(page.locator("table")).toBeVisible();
    await expect(page.locator("th:has-text('Email')")).toBeVisible();
    await expect(page.locator("th:has-text('Name')")).toBeVisible();
    await expect(page.locator("th:has-text('Status')")).toBeVisible();
  });

  test("can search users", async ({ page }) => {
    const searchInput = page.locator('input[placeholder*="Search"]');
    await expect(searchInput).toBeVisible();

    await searchInput.fill("test");
    await expect(page.locator("text=Loading...")).toBeVisible();
  });

  test("can filter by status", async ({ page }) => {
    const statusFilter = page.locator('select:has-text("Status")');
    await expect(statusFilter).toBeVisible();
  });

  test("can view user details", async ({ page }) => {
    await page.click('button:has-text("View"):first');
    await expect(page.locator("text=User Details")).toBeVisible();
  });
});

test.describe("Admin Teams Management", () => {
  test.beforeEach(async ({ page }) => {
    // Login as admin
    await page.goto(`${ADMIN_URL}/login`);
    await page.fill('input[type="email"]', "admin@test.com");
    await page.fill('input[type="password"]', "correctpassword");
    await page.click('button:has-text("Login")');
    await page.waitForURL(`${ADMIN_URL}/`);

    // Navigate to teams
    await page.click('a:has-text("Teams")');
    await page.waitForURL(`${ADMIN_URL}/teams`);
  });

  test("displays teams list", async ({ page }) => {
    await expect(page.locator("table")).toBeVisible();
    await expect(page.locator("th:has-text('Name')")).toBeVisible();
    await expect(page.locator("th:has-text('Members')")).toBeVisible();
    await expect(page.locator("th:has-text('Jobs')")).toBeVisible();
  });

  test("can search teams", async ({ page }) => {
    const searchInput = page.locator('input[placeholder*="Search"]');
    await expect(searchInput).toBeVisible();
  });
});

test.describe("Admin Jobs Management", () => {
  test.beforeEach(async ({ page }) => {
    // Login as admin
    await page.goto(`${ADMIN_URL}/login`);
    await page.fill('input[type="email"]', "admin@test.com");
    await page.fill('input[type="password"]', "correctpassword");
    await page.click('button:has-text("Login")');
    await page.waitForURL(`${ADMIN_URL}/`);

    // Navigate to jobs
    await page.click('a:has-text("Jobs")');
    await page.waitForURL(`${ADMIN_URL}/jobs`);
  });

  test("displays jobs list", async ({ page }) => {
    await expect(page.locator("table")).toBeVisible();
    await expect(page.locator("th:has-text('ID')")).toBeVisible();
    await expect(page.locator("th:has-text('Team')")).toBeVisible();
    await expect(page.locator("th:has-text('Status')")).toBeVisible();
  });

  test("can retry failed job", async ({ page }) => {
    // Find a failed job and click retry
    const retryButton = page.locator('button:has-text("Retry"):first');
    await expect(retryButton).toBeVisible();

    await retryButton.click();
    await expect(page.locator("text=Job queued for retry")).toBeVisible();
  });

  test("can cancel running job", async ({ page }) => {
    const cancelButton = page.locator('button:has-text("Cancel"):first');
    await expect(cancelButton).toBeVisible();

    await cancelButton.click();
    await expect(page.locator("text=Job cancellation requested")).toBeVisible();
  });
});

test.describe("Admin Analytics", () => {
  test.beforeEach(async ({ page }) => {
    // Login as admin
    await page.goto(`${ADMIN_URL}/login`);
    await page.fill('input[type="email"]', "admin@test.com");
    await page.fill('input[type="password"]', "correctpassword");
    await page.click('button:has-text("Login")');
    await page.waitForURL(`${ADMIN_URL}/`);

    // Navigate to analytics
    await page.click('a:has-text("Analytics")');
    await page.waitForURL(`${ADMIN_URL}/analytics`);
  });

  test("displays usage chart", async ({ page }) => {
    await expect(page.locator("text=Jobs per Day")).toBeVisible();
    await expect(page.locator("canvas")).toBeVisible();
  });

  test("displays language distribution", async ({ page }) => {
    await expect(page.locator("text=Languages")).toBeVisible();
    await expect(page.locator("canvas")).toBeVisible();
  });
});

test.describe("Admin Audit Logs", () => {
  test.beforeEach(async ({ page }) => {
    // Login as admin
    await page.goto(`${ADMIN_URL}/login`);
    await page.fill('input[type="email"]', "admin@test.com");
    await page.fill('input[type="password"]', "correctpassword");
    await page.click('button:has-text("Login")');
    await page.waitForURL(`${ADMIN_URL}/`);

    // Navigate to audit logs
    await page.click('a:has-text("Audit Logs")');
    await page.waitForURL(`${ADMIN_URL}/audit-logs`);
  });

  test("displays audit logs table", async ({ page }) => {
    await expect(page.locator("table")).toBeVisible();
    await expect(page.locator("th:has-text('Admin')")).toBeVisible();
    await expect(page.locator("th:has-text('Action')")).toBeVisible();
    await expect(page.locator("th:has-text('Timestamp')")).toBeVisible();
  });

  test("can filter by action type", async ({ page }) => {
    const actionFilter = page.locator('select:has-text("Action")');
    await expect(actionFilter).toBeVisible();
  });
});

test.describe("Admin Navigation", () => {
  test.beforeEach(async ({ page }) => {
    // Login as admin
    await page.goto(`${ADMIN_URL}/login`);
    await page.fill('input[type="email"]', "admin@test.com");
    await page.fill('input[type="password"]', "correctpassword");
    await page.click('button:has-text("Login")');
    await page.waitForURL(`${ADMIN_URL}/`);
  });

  test("sidebar navigation works", async ({ page }) => {
    const sidebar = page.locator("aside");
    await expect(sidebar).toBeVisible();

    // Click through navigation items
    await page.click('a:has-text("Users")');
    await expect(page).toHaveURL(/\/users$/);

    await page.click('a:has-text("Teams")');
    await expect(page).toHaveURL(/\/teams$/);

    await page.click('a:has-text("Jobs")');
    await expect(page).toHaveURL(/\/jobs$/);

    await page.click('a:has-text("Analytics")');
    await expect(page).toHaveURL(/\/analytics$/);
  });

  test("logout works", async ({ page }) => {
    const logoutButton = page.locator('button:has-text("Logout")');
    await expect(logoutButton).toBeVisible();

    await logoutButton.click();
    await expect(page).toHaveURL(/\/login$/);
  });
});
