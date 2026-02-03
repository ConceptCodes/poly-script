import { describe, expect, it, vi, beforeEach } from "vitest";
import { apiFetch } from "../lib/api";
import { API_URL } from "@poly/ui";

// Mock fetch globally
const mockFetch = vi.fn();
global.fetch = mockFetch as unknown as typeof fetch;

// Mock localStorage
const mockLocalStorage = {
  getItem: vi.fn(),
  setItem: vi.fn(),
  removeItem: vi.fn(),
};
global.localStorage = mockLocalStorage as unknown as Storage;

describe("Admin apiFetch", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe("Authorization header", () => {
    it("should use admin_access_token from localStorage", async () => {
      mockLocalStorage.getItem.mockReturnValue("admin-token-456");
      mockFetch.mockResolvedValue({
        ok: true,
        json: async () => ({ success: true }),
      });

      await apiFetch("/test");

      expect(mockFetch).toHaveBeenCalledWith(
        `${API_URL}/test`,
        expect.objectContaining({
          headers: expect.objectContaining({
            Authorization: "Bearer admin-token-456",
          }),
        }),
      );
    });

    it("should use admin_access_token key (not access_token)", async () => {
      mockLocalStorage.getItem.mockImplementation((key: string) => {
        return key === "admin_access_token" ? "admin-token" : null;
      });
      mockFetch.mockResolvedValue({
        ok: true,
        json: async () => ({ success: true }),
      });

      await apiFetch("/test");

      expect(mockLocalStorage.getItem).toHaveBeenCalledWith("admin_access_token");
      expect(mockLocalStorage.getItem).not.toHaveBeenCalledWith("access_token");
    });
  });

  describe("Error handling", () => {
    it("should throw Error object (not error object)", async () => {
      mockLocalStorage.getItem.mockReturnValue("admin-token");
      mockFetch.mockResolvedValue({
        ok: false,
        status: 400,
        json: async () => ({ detail: "Bad request" }),
      });

      await expect(apiFetch("/test")).rejects.toThrow(Error);
      await expect(apiFetch("/test")).rejects.toThrow("Bad request");
    });

    it("should use default message when error response has no detail field", async () => {
      mockLocalStorage.getItem.mockReturnValue("admin-token");
      mockFetch.mockResolvedValue({
        ok: false,
        status: 500,
        json: async () => ({}),
      });

      await expect(apiFetch("/test")).rejects.toThrow("An unknown error occurred");
    });

    it("should use default message when json parsing fails", async () => {
      mockLocalStorage.getItem.mockReturnValue("admin-token");
      mockFetch.mockResolvedValue({
        ok: false,
        status: 500,
        json: async () => {
          throw new Error("Invalid JSON");
        },
      });

      await expect(apiFetch("/test")).rejects.toThrow("An unknown error occurred");
    });
  });

  describe("Success cases", () => {
    it("should return parsed JSON on successful response", async () => {
      mockLocalStorage.getItem.mockReturnValue("admin-token");
      mockFetch.mockResolvedValue({
        ok: true,
        json: async () => ({ data: "admin-value" }),
      });

      const result = await apiFetch("/test");
      expect(result).toEqual({ data: "admin-value" });
    });

    it("should handle empty JSON response", async () => {
      mockLocalStorage.getItem.mockReturnValue("admin-token");
      mockFetch.mockResolvedValue({
        ok: true,
        json: async () => {
          throw new Error("No JSON");
        },
      });

      const result = await apiFetch("/test");
      expect(result).toEqual({});
    });
  });
});
