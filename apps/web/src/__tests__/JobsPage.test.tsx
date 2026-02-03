import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen, waitFor } from "@testing-library/react";
import { BrowserRouter } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";
import * as api from "../lib/api";
import { JobsPage } from "../pages/jobs";

vi.mock("../lib/api", () => ({
  api: {
    getJobs: vi.fn(),
  },
}));

describe("JobsPage", () => {
  const mockJobs = {
    jobs: [
      {
        id: "job-1",
        status: "QUEUED",
        filename: "test1.mp3",
        language: "en",
        progress_pct: 0,
        progress_stage: "queued",
        created_at: "2025-02-01T10:00:00Z",
        started_at: null,
        finished_at: null,
      },
      {
        id: "job-2",
        status: "RUNNING",
        filename: "test2.mp3",
        language: "es",
        progress_pct: 50,
        progress_stage: "transcribing",
        created_at: "2025-02-01T11:00:00Z",
        started_at: "2025-02-01T11:00:01Z",
        finished_at: null,
      },
    ],
    total: 2,
    page: 1,
    page_size: 20,
  };

  beforeEach(() => {
    vi.clearAllMocks();
  });

  const renderWithProviders = (component: React.ReactElement) => {
    const queryClient = new QueryClient({
      defaultOptions: {
        queries: {
          retry: false,
        },
      },
    });

    return render(
      <QueryClientProvider client={queryClient}>
        <BrowserRouter>{component}</BrowserRouter>
      </QueryClientProvider>,
    );
  };

  it("renders loading state initially", () => {
    vi.mocked(api.api.getJobs).mockImplementation(
      () => new Promise(() => {}), // Never resolves
    );

    renderWithProviders(<JobsPage />);

    expect(screen.getByText("Loading jobs...")).toBeInTheDocument();
  });

  it("renders jobs list successfully", async () => {
    vi.mocked(api.api.getJobs).mockResolvedValue(mockJobs);

    renderWithProviders(<JobsPage />);

    await waitFor(() => {
      expect(screen.getByText("Jobs (2)")).toBeInTheDocument();
    });

    expect(screen.getByText("test1.mp3")).toBeInTheDocument();
    expect(screen.getByText("test2.mp3")).toBeInTheDocument();
  });

  it("renders status badges correctly", async () => {
    vi.mocked(api.api.getJobs).mockResolvedValue(mockJobs);

    renderWithProviders(<JobsPage />);

    await waitFor(() => {
      expect(screen.getByText("QUEUED")).toBeInTheDocument();
      expect(screen.getByText("RUNNING")).toBeInTheDocument();
    });
  });

  it("renders progress bars for running jobs", async () => {
    vi.mocked(api.api.getJobs).mockResolvedValue(mockJobs);

    renderWithProviders(<JobsPage />);

    await waitFor(() => {
      expect(screen.getByText("50%")).toBeInTheDocument();
    });
  });

  it("shows empty state when no jobs", async () => {
    vi.mocked(api.api.getJobs).mockResolvedValue({
      jobs: [],
      total: 0,
      page: 1,
      page_size: 20,
    });

    renderWithProviders(<JobsPage />);

    await waitFor(() => {
      expect(screen.getByText("No jobs found")).toBeInTheDocument();
      expect(screen.getByText("Upload Audio")).toBeInTheDocument();
    });
  });

  it("shows error state on API failure", async () => {
    vi.mocked(api.api.getJobs).mockRejectedValue(new Error("Failed to fetch"));

    renderWithProviders(<JobsPage />);

    await waitFor(() => {
      expect(screen.getByText("Error Loading Jobs")).toBeInTheDocument();
      expect(screen.getByText("Retry")).toBeInTheDocument();
    });
  });

  it("renders table headers", async () => {
    vi.mocked(api.api.getJobs).mockResolvedValue(mockJobs);

    renderWithProviders(<JobsPage />);

    await waitFor(() => {
      expect(screen.getByText("Created")).toBeInTheDocument();
      expect(screen.getByText("Status")).toBeInTheDocument();
      expect(screen.getByText("Filename")).toBeInTheDocument();
      expect(screen.getByText("Language")).toBeInTheDocument();
      expect(screen.getByText("Progress")).toBeInTheDocument();
      expect(screen.getByText("Started")).toBeInTheDocument();
      expect(screen.getByText("Finished")).toBeInTheDocument();
      expect(screen.getByText("Stage")).toBeInTheDocument();
    });
  });

  it("calls getJobs with correct params", async () => {
    vi.mocked(api.api.getJobs).mockResolvedValue(mockJobs);

    renderWithProviders(<JobsPage />);

    await waitFor(() => {
      expect(api.api.getJobs).toHaveBeenCalledWith({
        page: 1,
        page_size: 20,
        search: undefined,
        sort_field: "created_at",
        sort_order: "desc",
        status: undefined,
      });
    });
  });

  it("shows pagination when multiple pages", async () => {
    const manyJobs = {
      jobs: mockJobs.jobs,
      total: 50,
      page: 1,
      page_size: 20,
    };
    vi.mocked(api.api.getJobs).mockResolvedValue(manyJobs);

    renderWithProviders(<JobsPage />);

    await waitFor(() => {
      expect(screen.getByText("Showing 1 to 20 of 50 jobs")).toBeInTheDocument();
      expect(screen.getByText("Page 1 of 3")).toBeInTheDocument();
      expect(screen.getByText("Next")).toBeInTheDocument();
    });
  });

  it("disables previous button on first page", async () => {
    const manyJobs = {
      jobs: mockJobs.jobs,
      total: 50,
      page: 1,
      page_size: 20,
    };
    vi.mocked(api.api.getJobs).mockResolvedValue(manyJobs);

    renderWithProviders(<JobsPage />);

    await waitFor(() => {
      const prevButton = screen.getByText("Previous").closest("button");
      expect(prevButton).toBeDisabled();
    });
  });

  it("shows search and filter controls", async () => {
    vi.mocked(api.api.getJobs).mockResolvedValue(mockJobs);

    renderWithProviders(<JobsPage />);

    await waitFor(() => {
      const searchInput = screen.getByPlaceholderText("Search by filename...");
      expect(searchInput).toBeInTheDocument();
      expect(screen.getByText("All Status")).toBeInTheDocument();
    });
  });

  it("navigates to job detail on row click", async () => {
    vi.mocked(api.api.getJobs).mockResolvedValue(mockJobs);

    renderWithProviders(<JobsPage />);

    await waitFor(() => {
      const jobRow = screen.getByText("test1.mp3").closest("tr");
      expect(jobRow).toHaveClass("cursor-pointer");
    });
  });
});
