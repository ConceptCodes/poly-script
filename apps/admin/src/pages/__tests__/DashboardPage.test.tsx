import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import { DashboardPage } from "../DashboardPage";

vi.mock("../../lib/api", () => ({
  apiFetch: vi.fn().mockResolvedValue({}),
}));

describe("DashboardPage", () => {
  it("renders dashboard title", () => {
    render(<DashboardPage />);
    expect(screen.getByText("Dashboard")).toBeInTheDocument();
  });

  it("renders stat card labels", () => {
    render(<DashboardPage />);
    expect(screen.getByText("Users")).toBeInTheDocument();
    expect(screen.getByText("Teams")).toBeInTheDocument();
    expect(screen.getByText("Jobs")).toBeInTheDocument();
    expect(screen.getByText("Admins")).toBeInTheDocument();
  });

  it("renders system health section", () => {
    render(<DashboardPage />);
    expect(screen.getByText("System Health")).toBeInTheDocument();
  });
});
