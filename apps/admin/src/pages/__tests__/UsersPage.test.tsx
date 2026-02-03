import { render, screen } from "@testing-library/react";
import { BrowserRouter } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { UsersPage } from "../UsersPage";

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

describe("UsersPage", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("renders users page title", () => {
    render(
      <Wrapper>
        <UsersPage />
      </Wrapper>,
    );
    expect(screen.getByText("Users")).toBeInTheDocument();
  });

  it("renders search input", () => {
    render(
      <Wrapper>
        <UsersPage />
      </Wrapper>,
    );
    expect(screen.getByPlaceholderText("Search by email or name")).toBeInTheDocument();
  });

  it("renders filter buttons", () => {
    render(
      <Wrapper>
        <UsersPage />
      </Wrapper>,
    );
    expect(screen.getByText("All")).toBeInTheDocument();
    expect(screen.getByText("Active")).toBeInTheDocument();
    expect(screen.getAllByText("Suspended")).toHaveLength(2);
    expect(screen.getByText("Unverified")).toBeInTheDocument();
  });

  it("renders refresh button", () => {
    render(
      <Wrapper>
        <UsersPage />
      </Wrapper>,
    );
    expect(screen.getByText("Refresh")).toBeInTheDocument();
  });
});
