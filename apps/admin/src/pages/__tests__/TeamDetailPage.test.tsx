import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import { TeamDetailPage } from "../TeamDetailPage";
import { BrowserRouter, Routes, Route } from "react-router-dom";

vi.mock("../../lib/api", () => ({
  apiFetch: vi.fn().mockResolvedValue({
    id: "test-id",
    name: "Test Team",
    plan: "STANDARD",
    owner_id: "owner-id",
    owner_email: "owner@example.com",
    created_at: new Date().toISOString(),
    members: [],
    usage: {
      jobs_used: 50,
      jobs_limit: 100,
      members_used: 2,
      members_limit: 5,
      reset_date: new Date().toISOString(),
    },
  }),
}));

function Wrapper({ children }: { children: React.ReactNode }) {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/teams/:id" element={children} />
      </Routes>
    </BrowserRouter>
  );
}

describe("TeamDetailPage", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("renders team details title", () => {
    render(
      <Wrapper>
        <TeamDetailPage />
      </Wrapper>,
    );
    expect(screen.getByText("Team Details")).toBeInTheDocument();
  });

  it("renders team information section", async () => {
    render(
      <Wrapper>
        <TeamDetailPage />
      </Wrapper>,
    );
    screen.getByText("Team Information");
    expect(screen.getByText("Team Name")).toBeInTheDocument();
    expect(screen.getByText("Plan")).toBeInTheDocument();
    expect(screen.getByText("Owner Email")).toBeInTheDocument();
    expect(screen.getByText("Created At")).toBeInTheDocument();
  });

  it("renders usage & limits section", async () => {
    render(
      <Wrapper>
        <TeamDetailPage />
      </Wrapper>,
    );
    screen.getByText("Usage & Limits");
    expect(screen.getByText("Jobs Used")).toBeInTheDocument();
    expect(screen.getByText("Members Used")).toBeInTheDocument();
    expect(screen.getByText("Reset Date")).toBeInTheDocument();
  });
});
