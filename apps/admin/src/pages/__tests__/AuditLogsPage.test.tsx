import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import { AuditLogsPage } from "../AuditLogsPage";

vi.mock("../../lib/api", () => ({
  apiFetch: vi.fn().mockResolvedValue({ items: [] }),
}));

describe("AuditLogsPage", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("renders audit logs page title", () => {
    render(<AuditLogsPage />);
    expect(screen.getByText("Audit Logs")).toBeInTheDocument();
  });

  it("renders search input", () => {
    render(<AuditLogsPage />);
    expect(screen.getByPlaceholderText("Search by admin email or resource")).toBeInTheDocument();
  });

  it("renders action filter buttons", () => {
    render(<AuditLogsPage />);
    expect(screen.getByText("All Actions")).toBeInTheDocument();
    expect(screen.getByText("Create")).toBeInTheDocument();
    expect(screen.getByText("Update")).toBeInTheDocument();
    expect(screen.getByText("Delete")).toBeInTheDocument();
    expect(screen.getByText("Suspend")).toBeInTheDocument();
    expect(screen.getByText("Unsuspend")).toBeInTheDocument();
    expect(screen.getByText("Retry")).toBeInTheDocument();
    expect(screen.getByText("Cancel")).toBeInTheDocument();
  });

  it("renders resource filter buttons", () => {
    render(<AuditLogsPage />);
    expect(screen.getByText("All Resources")).toBeInTheDocument();
    expect(screen.getByText("User")).toBeInTheDocument();
    expect(screen.getByText("Team")).toBeInTheDocument();
    expect(screen.getByText("Job")).toBeInTheDocument();
    expect(screen.getByText("Settings")).toBeInTheDocument();
  });

  it("renders refresh button", () => {
    render(<AuditLogsPage />);
    expect(screen.getByText("Refresh")).toBeInTheDocument();
  });

  it("renders table headers", () => {
    render(<AuditLogsPage />);
    expect(screen.getByText("Timestamp")).toBeInTheDocument();
    expect(screen.getByText("Admin")).toBeInTheDocument();
    expect(screen.getByText("Action")).toBeInTheDocument();
    expect(screen.getByText("Resource Type")).toBeInTheDocument();
    expect(screen.getByText("Resource ID")).toBeInTheDocument();
    expect(screen.getByText("IP Address")).toBeInTheDocument();
    expect(screen.getByText("Details")).toBeInTheDocument();
  });
});
