import { render, screen } from "@testing-library/react";
import { BrowserRouter } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { TeamsPage } from "../TeamsPage";

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

describe("TeamsPage", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("renders teams page title", () => {
    render(
      <Wrapper>
        <TeamsPage />
      </Wrapper>,
    );
    expect(screen.getByText("Teams")).toBeInTheDocument();
  });

  it("renders search input", () => {
    render(
      <Wrapper>
        <TeamsPage />
      </Wrapper>,
    );
    expect(screen.getByPlaceholderText("Search by team name or owner email")).toBeInTheDocument();
  });

  it("renders plan filter buttons", () => {
    render(
      <Wrapper>
        <TeamsPage />
      </Wrapper>,
    );
    expect(screen.getByText("All Plans")).toBeInTheDocument();
    expect(screen.getByText("FREE")).toBeInTheDocument();
    expect(screen.getByText("STANDARD")).toBeInTheDocument();
    expect(screen.getByText("PRO")).toBeInTheDocument();
  });

  it("renders refresh button", () => {
    render(
      <Wrapper>
        <TeamsPage />
      </Wrapper>,
    );
    expect(screen.getByText("Refresh")).toBeInTheDocument();
  });
});
