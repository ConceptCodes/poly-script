import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import { JobDetailPage } from "../JobDetailPage";
import { BrowserRouter, Routes, Route } from "react-router-dom";

vi.mock("../../lib/api", () => ({
  apiFetch: vi.fn().mockResolvedValue({
    id: "test-job-id",
    filename: "test.mp3",
    status: "SUCCEEDED",
    language: "en",
    engine: "whisper",
    created_at: new Date().toISOString(),
    started_at: new Date().toISOString(),
    completed_at: new Date().toISOString(),
    duration_ms: 5000,
    attempts: 1,
  }),
}));

function Wrapper({ children }: { children: React.ReactNode }) {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/jobs/:id" element={children} />
      </Routes>
    </BrowserRouter>
  );
}

describe("JobDetailPage", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("renders job details title", async () => {
    render(
      <Wrapper>
        <JobDetailPage />
      </Wrapper>,
    );
    screen.getByText("Job Details");
  });

  it("renders job information section", async () => {
    render(
      <Wrapper>
        <JobDetailPage />
      </Wrapper>,
    );
    screen.getByText("Job Information");
    expect(screen.getByText("Filename")).toBeInTheDocument();
    expect(screen.getByText("Status")).toBeInTheDocument();
    expect(screen.getByText("Engine")).toBeInTheDocument();
    expect(screen.getByText("Language")).toBeInTheDocument();
  });

  it("renders timeline section", async () => {
    render(
      <Wrapper>
        <JobDetailPage />
      </Wrapper>,
    );
    screen.getByText("Timeline");
    expect(screen.getByText("Created At")).toBeInTheDocument();
    expect(screen.getByText("Started At")).toBeInTheDocument();
    expect(screen.getByText("Completed At")).toBeInTheDocument();
    expect(screen.getByText("Duration")).toBeInTheDocument();
  });
});
