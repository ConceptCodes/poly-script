import { render, screen } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { TeamDetailPage } from "../TeamDetailPage";

const mockTeam = {
  id: "test-team-id",
  name: "Test Team",
  plan: "STANDARD" as const,
  owner_id: "owner-id",
  owner_email: "owner@example.com",
  created_at: "2024-01-01T00:00:00Z",
  members: [],
  usage: {
    jobs_used: 10,
    jobs_limit: 25,
    members_used: 3,
    members_limit: 5,
    reset_date: "2024-02-01T00:00:00Z",
  },
};

vi.mock("../../lib/api", () => ({
  apiFetch: vi.fn().mockImplementation((url: string) => {
    if (url.includes("/admin/teams/")) {
      return Promise.resolve(mockTeam);
    }
    return Promise.resolve({});
  }),
}));

const mockNavigate = vi.fn();
vi.mock("react-router-dom", async () => {
  const actual = await vi.importActual("react-router-dom");
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  };
});

function Wrapper({
  children,
  initialEntry = "/teams/test-team-id",
}: {
  children: React.ReactNode;
  initialEntry?: string;
}) {
  return (
    <MemoryRouter initialEntries={[initialEntry]}>
      <Routes>
        <Route path="/teams/:id" element={children} />
      </Routes>
    </MemoryRouter>
  );
}

describe("TeamDetailPage", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("renders loading state initially", () => {
    render(
      <Wrapper>
        <TeamDetailPage />
      </Wrapper>,
    );
    expect(screen.getByText("Loading…")).toBeInTheDocument();
  });

  it("renders team details after loading", async () => {
    render(
      <Wrapper>
        <TeamDetailPage />
      </Wrapper>,
    );

    // Wait for team data to load
    expect(await screen.findByText("Team Details")).toBeInTheDocument();
    expect(await screen.findByText("Test Team")).toBeInTheDocument();
    expect(await screen.findByText("owner@example.com")).toBeInTheDocument();
  });

  it("renders back button", async () => {
    render(
      <Wrapper>
        <TeamDetailPage />
      </Wrapper>,
    );

    const backButton = await screen.findByLabelText("Back to teams");
    expect(backButton).toBeInTheDocument();
  });

  it("renders plan badge", async () => {
    render(
      <Wrapper>
        <TeamDetailPage />
      </Wrapper>,
    );

    expect(await screen.findByText("Standard")).toBeInTheDocument();
  });

  it("renders usage information", async () => {
    render(
      <Wrapper>
        <TeamDetailPage />
      </Wrapper>,
    );

    expect(await screen.findByText("Usage & Limits")).toBeInTheDocument();
    expect(await screen.findByText("Jobs Used")).toBeInTheDocument();
    expect(await screen.findByText("Members Used")).toBeInTheDocument();
  });
});
