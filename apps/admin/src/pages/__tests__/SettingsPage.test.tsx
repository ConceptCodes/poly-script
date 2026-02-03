import { render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { SettingsPage } from "../SettingsPage";

vi.mock("../../lib/api", () => ({
  apiFetch: vi.fn().mockResolvedValue({ administrators: [], system: {} }),
}));

describe("SettingsPage", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("renders settings page title", () => {
    render(<SettingsPage />);
    expect(screen.getByText("System Settings")).toBeInTheDocument();
  });

  it("renders administrators section", () => {
    render(<SettingsPage />);
    expect(screen.getByText("Administrators")).toBeInTheDocument();
  });

  it("renders settings tabs", () => {
    render(<SettingsPage />);
    expect(screen.getByText("Engines")).toBeInTheDocument();
    expect(screen.getByText("Storage")).toBeInTheDocument();
    expect(screen.getByText("Rate Limits")).toBeInTheDocument();
    expect(screen.getByText("Email")).toBeInTheDocument();
    expect(screen.getByText("Advanced")).toBeInTheDocument();
  });

  it("renders save settings button", () => {
    render(<SettingsPage />);
    expect(screen.getByText("Save Settings")).toBeInTheDocument();
  });
});
