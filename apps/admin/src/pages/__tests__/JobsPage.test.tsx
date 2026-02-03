import { render, screen } from "@testing-library/react";
import { BrowserRouter } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { JobsPage } from "../JobsPage";

vi.mock("../../lib/api", () => ({
  apiFetch: vi.fn().mockResolvedValue({ items: [] }),
}));

const mockNavigate = vi.fn();
vi.mock("react-router-dom", async () => {
  const actual = await vi.importActual("react-router-dom");
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  };
});

function Wrapper({ children }: { children: React.ReactNode }) {
  return <BrowserRouter>{children}</BrowserRouter>;
}

describe("JobsPage", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("renders jobs page title", () => {
    render(
      <Wrapper>
        <JobsPage />
      </Wrapper>,
    );
    expect(screen.getByText("Jobs")).toBeInTheDocument();
  });

  it("renders search input", () => {
    render(
      <Wrapper>
        <JobsPage />
      </Wrapper>,
    );
    expect(screen.getByPlaceholderText("Search by filename")).toBeInTheDocument();
  });

  it("renders status filter buttons", () => {
    render(
      <Wrapper>
        <JobsPage />
      </Wrapper>,
    );
    expect(screen.getByText("All Status")).toBeInTheDocument();
    expect(screen.getByText("QUEUED")).toBeInTheDocument();
    expect(screen.getByText("RUNNING")).toBeInTheDocument();
    expect(screen.getByText("SUCCEEDED")).toBeInTheDocument();
    expect(screen.getByText("FAILED")).toBeInTheDocument();
    expect(screen.getByText("CANCELED")).toBeInTheDocument();
  });

  it("renders engine filter buttons", () => {
    render(
      <Wrapper>
        <JobsPage />
      </Wrapper>,
    );
    expect(screen.getByText("All Engines")).toBeInTheDocument();
    expect(screen.getByText("whisper")).toBeInTheDocument();
    expect(screen.getByText("speechmatics")).toBeInTheDocument();
    expect(screen.getByText("assemblyai")).toBeInTheDocument();
  });

  it("renders refresh button", () => {
    render(
      <Wrapper>
        <JobsPage />
      </Wrapper>,
    );
    expect(screen.getByText("Refresh")).toBeInTheDocument();
  });
});
