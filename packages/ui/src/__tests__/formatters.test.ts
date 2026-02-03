import { describe, expect, it } from "vitest";
import { formatDate, formatTime, formatDateTime, formatNumber } from "../lib/formatters";

describe("Formatters", () => {
  describe("formatDate", () => {
    it("should format a date string in short format (Month Day, Year)", () => {
      const result = formatDate("2026-02-03T12:00:00Z");
      expect(result).toMatch(/Feb 3, 2026/);
    });

    it("should format a Date object", () => {
      const result = formatDate(new Date("2026-12-25T00:00:00Z"));
      expect(result).toMatch(/Dec 25, 2026/);
    });
  });

  describe("formatTime", () => {
    it("should format a date string as time", () => {
      const result = formatTime("2026-02-03T14:30:45Z");
      expect(result).toMatch(/2:30:45/);
    });

    it("should format a Date object as time", () => {
      const result = formatTime(new Date("2026-02-03T23:59:59Z"));
      expect(result).toMatch(/11:59:59/);
    });
  });

  describe("formatDateTime", () => {
    it("should format a date string as date and time", () => {
      const result = formatDateTime("2026-02-03T14:30:00Z");
      expect(result).toMatch(/Feb 3, 2026/);
      expect(result).toMatch(/2:30/);
    });

    it("should format a Date object as date and time", () => {
      const result = formatDateTime(new Date("2026-06-15T09:15:00Z"));
      expect(result).toMatch(/Jun 15, 2026/);
      expect(result).toMatch(/9:15/);
    });
  });

  describe("formatNumber", () => {
    it("should format a number with thousands separator", () => {
      const result = formatNumber(1234567);
      expect(result).toBe("1,234,567");
    });

    it("should format a decimal number", () => {
      const result = formatNumber(1234.56);
      expect(result).toBe("1,234.56");
    });

    it("should format zero", () => {
      const result = formatNumber(0);
      expect(result).toBe("0");
    });

    it("should format negative numbers", () => {
      const result = formatNumber(-9876);
      expect(result).toBe("-9,876");
    });
  });
});
