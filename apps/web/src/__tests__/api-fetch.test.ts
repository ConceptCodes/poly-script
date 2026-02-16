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

describe("Web apiFetch", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe("Authorization header", () => {
    it("should use access_token from localStorage", async () => {
      mockLocalStorage.getItem.mockReturnValue("test-token-123");
      mockFetch.mockResolvedValue({
        ok: true,
        json: async () => ({ success: true }),
      });

      await apiFetch("/test");

      expect(mockFetch).toHaveBeenCalledWith(
        `${API_URL}/test`,
        expect.objectContaining({
          headers: expect.objectContaining({
            Authorization: "Bearer test-token-123",
          }),
        }),
      );
    });

    it("should use access_token key (not admin_access_token)", async () => {
      mockLocalStorage.getItem.mockImplementation((key: string) => {
        return key === "access_token" ? "web-token" : null;
      });
      mockFetch.mockResolvedValue({
        ok: true,
        json: async () => ({ success: true }),
      });

      await apiFetch("/test");

      expect(mockLocalStorage.getItem).toHaveBeenCalledWith("access_token");
      expect(mockLocalStorage.getItem).not.toHaveBeenCalledWith("admin_access_token");
    });
  });

  describe("FormData handling", () => {
    it("should pass FormData without Content-Type header", async () => {
      mockLocalStorage.getItem.mockReturnValue("token");
      mockFetch.mockResolvedValue({
        ok: true,
        json: async () => ({ success: true }),
      });

      const formData = new FormData();
      formData.append("file", new Blob(["test"]), "test.mp3");

      await apiFetch("/upload", {
        method: "POST",
        body: formData,
      });

      const fetchCall = mockFetch.mock.calls[0];
      expect(fetchCall[1].headers["Content-Type"]).toBeUndefined();
      expect(fetchCall[1].body).toBeInstanceOf(FormData);
    });

    it("should set Content-Type application/json for regular objects", async () => {
      mockLocalStorage.getItem.mockReturnValue("token");
      mockFetch.mockResolvedValue({
        ok: true,
        json: async () => ({ success: true }),
      });

      await apiFetch("/data", {
        method: "POST",
        body: { name: "test" },
      });

      const fetchCall = mockFetch.mock.calls[0];
      expect(fetchCall[1].headers["Content-Type"]).toBe("application/json");
    });
  });

  describe("Error handling", () => {
    it("should return error object with status and code", async () => {
      mockLocalStorage.getItem.mockReturnValue("token");
      mockFetch.mockResolvedValue({
        ok: false,
        status: 400,
        json: async () => ({ error: { message: "Bad request", code: "INVALID_INPUT" } }),
      });

      await expect(apiFetch("/test")).rejects.toEqual({
        message: "Bad request",
        code: "INVALID_INPUT",
        status: 400,
        details: null,
        request_id: null,
        documentation_url: null,
      });
    });

    it("should include null code when error response has no code field", async () => {
      mockLocalStorage.getItem.mockReturnValue("token");
      mockFetch.mockResolvedValue({
        ok: false,
        status: 500,
        json: async () => ({ error: { message: "Server error" } }),
      });

      await expect(apiFetch("/test")).rejects.toEqual({
        message: "Server error",
        code: null,
        status: 500,
        details: null,
        request_id: null,
        documentation_url: null,
      });
    });

    it("should use default message when json parsing fails", async () => {
      mockLocalStorage.getItem.mockReturnValue("token");
      mockFetch.mockResolvedValue({
        ok: false,
        status: 500,
        json: async () => {
          throw new Error("Invalid JSON");
        },
      });

      await expect(apiFetch("/test")).rejects.toEqual({
        message: "An unknown error occurred",
        code: null,
        status: 500,
        details: null,
        request_id: null,
        documentation_url: null,
      });
    });
  });

  describe("Success cases", () => {
    it("should return parsed JSON on successful response", async () => {
      mockLocalStorage.getItem.mockReturnValue("token");
      mockFetch.mockResolvedValue({
        ok: true,
        json: async () => ({ data: "test-value" }),
      });

      const result = await apiFetch("/test");
      expect(result).toEqual({ data: "test-value" });
    });

    it("should handle empty JSON response", async () => {
      mockLocalStorage.getItem.mockReturnValue("token");
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
