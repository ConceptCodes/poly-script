import "../i18n/config";
import { expect, afterEach, vi } from "vitest";
import { cleanup } from "@testing-library/react";
import * as matchers from "@testing-library/jest-dom/matchers";

// Mock localStorage
const localStorageMock = {
  getItem: vi.fn(() => null),
  setItem: vi.fn(),
  removeItem: vi.fn(),
  clear: vi.fn(),
  length: 0,
  key: vi.fn((index: number) => ""),
};
global.localStorage = localStorageMock as any;

// Cleanup after each test
afterEach(() => {
  cleanup();
  vi.clearAllMocks();
});

// Add custom matchers
expect.extend(matchers);
