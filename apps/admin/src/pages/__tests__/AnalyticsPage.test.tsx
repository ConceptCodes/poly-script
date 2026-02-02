import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import { AnalyticsPage } from "../AnalyticsPage";

vi.mock("../../lib/api", () => ({
  apiFetch: vi.fn().mockResolvedValue({}),
}));

describe("AnalyticsPage", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("renders analytics page title", () => {
    render(<AnalyticsPage />);
    expect(screen.getByText("Analytics")).toBeInTheDocument();
  });

  it("renders time range selector", () => {
    render(<AnalyticsPage />);
    expect(screen.getByText("7 days")).toBeInTheDocument();
    expect(screen.getByText("30 days")).toBeInTheDocument();
    expect(screen.getByText("90 days")).toBeInTheDocument();
    expect(screen.getByText("All time")).toBeInTheDocument();
  });

  it("renders metric cards", () => {
    render(<AnalyticsPage />);
    expect(screen.getByText("Users")).toBeInTheDocument();
    expect(screen.getByText("Teams")).toBeInTheDocument();
    expect(screen.getByText("Total Jobs")).toBeInTheDocument();
    expect(screen.getByText("Successful Jobs")).toBeInTheDocument();
  });

  it("renders error trends section", () => {
    render(<AnalyticsPage />);
    expect(screen.getByText("Error Trends")).toBeInTheDocument();
    expect(screen.getByText("Total Errors")).toBeInTheDocument();
    expect(screen.getByText("Failed Jobs")).toBeInTheDocument();
    expect(screen.getByText("Canceled Jobs")).toBeInTheDocument();
  });

  it("renders coming soon badges", () => {
    render(<AnalyticsPage />);
    expect(screen.getByText("Additional Metrics")).toBeInTheDocument();
    expect(screen.getByText("Avg. Job Duration")).toBeInTheDocument();
    expect(screen.getByText("Revenue (MTD)")).toBeInTheDocument();
    expect(screen.getByText("Active Subscriptions")).toBeInTheDocument();
    expect(screen.getByText("Churn Rate")).toBeInTheDocument();
  });
});
