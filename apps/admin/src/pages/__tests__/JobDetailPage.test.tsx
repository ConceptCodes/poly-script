import { render, screen } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { JobDetailPage } from "../JobDetailPage";

const mockJob = {
  id: "test-job-id",
  filename: "test-audio.mp3",
  status: "SUCCEEDED" as const,
  language: "en",
  engine: "whisper",
  created_at: "2024-01-01T00:00:00Z",
  started_at: "2024-01-01T00:01:00Z",
  completed_at: "2024-01-01T00:05:00Z",
  team_id: "team-id",
  team_name: "Test Team",
  progress: {
    stage: "completed",
    percent: 100,
  },
  attempts: 1,
  duration_ms: 240000,
};

vi.mock("../../lib/api", () => ({
  apiFetch: vi.fn().mockImplementation((url: string) => {
    if (url.includes("/admin/jobs/")) {
      return Promise.resolve(mockJob);
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
  initialEntry = "/jobs/test-job-id",
}: {
  children: React.ReactNode;
  initialEntry?: string;
}) {
  return (
    <MemoryRouter initialEntries={[initialEntry]}>
      <Routes>
        <Route path="/jobs/:id" element={children} />
      </Routes>
    </MemoryRouter>
  );
}

describe("JobDetailPage", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("renders loading state initially", () => {
    render(
      <Wrapper>
        <JobDetailPage />
      </Wrapper>,
    );
    expect(screen.getByText("Loading…")).toBeInTheDocument();
  });

  it("renders job details after loading", async () => {
    render(
      <Wrapper>
        <JobDetailPage />
      </Wrapper>,
    );

    // Wait for job data to load
    expect(await screen.findByText("Job Details")).toBeInTheDocument();
    expect(await screen.findByText("test-audio.mp3")).toBeInTheDocument();
    expect(await screen.findByText("Test Team")).toBeInTheDocument();
  });

  it("renders back button", async () => {
    render(
      <Wrapper>
        <JobDetailPage />
      </Wrapper>,
    );

    const backButton = await screen.findByLabelText("Back to jobs");
    expect(backButton).toBeInTheDocument();
  });

  it("renders status badge in header", async () => {
    render(
      <Wrapper>
        <JobDetailPage />
      </Wrapper>,
    );

    const succeededBadges = await screen.findAllByText("Succeeded");
    expect(succeededBadges.length).toBeGreaterThanOrEqual(1);
  });

  it("renders job ID", async () => {
    render(
      <Wrapper>
        <JobDetailPage />
      </Wrapper>,
    );

    expect(await screen.findByText("Job ID: test-job-id")).toBeInTheDocument();
  });

  it("renders timeline information", async () => {
    render(
      <Wrapper>
        <JobDetailPage />
      </Wrapper>,
    );

    expect(await screen.findByText("Timeline")).toBeInTheDocument();
    expect(await screen.findByText("Created At")).toBeInTheDocument();
    expect(await screen.findByText("Started At")).toBeInTheDocument();
    expect(await screen.findByText("Completed At")).toBeInTheDocument();
  });
});
