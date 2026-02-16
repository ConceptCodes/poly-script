import { render, screen } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { UserDetailPage } from "../UserDetailPage";

const mockUser = {
  id: "test-user-id",
  email: "test@example.com",
  full_name: "Test User",
  is_active: true,
  is_verified: true,
  is_suspended: false,
  created_at: "2024-01-01T00:00:00Z",
  last_login_at: "2024-01-02T00:00:00Z",
  teams: [],
};

vi.mock("../../lib/api", () => ({
  apiFetch: vi.fn().mockImplementation((url: string) => {
    if (url.includes("/admin/users/")) {
      return Promise.resolve(mockUser);
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
  initialEntry = "/users/test-user-id",
}: {
  children: React.ReactNode;
  initialEntry?: string;
}) {
  return (
    <MemoryRouter initialEntries={[initialEntry]}>
      <Routes>
        <Route path="/users/:id" element={children} />
      </Routes>
    </MemoryRouter>
  );
}

describe("UserDetailPage", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("renders loading state initially", () => {
    render(
      <Wrapper>
        <UserDetailPage />
      </Wrapper>,
    );
    expect(screen.getByText("Loading…")).toBeInTheDocument();
  });

  it("renders user details after loading", async () => {
    render(
      <Wrapper>
        <UserDetailPage />
      </Wrapper>,
    );

    // Wait for user data to load
    expect(await screen.findByText("User Details")).toBeInTheDocument();
    expect(await screen.findByText("test@example.com")).toBeInTheDocument();
    expect(await screen.findByText("Test User")).toBeInTheDocument();
  });

  it("renders back button", async () => {
    render(
      <Wrapper>
        <UserDetailPage />
      </Wrapper>,
    );

    const backButton = await screen.findByLabelText("Back to users");
    expect(backButton).toBeInTheDocument();
  });

  it("renders account status badges", async () => {
    render(
      <Wrapper>
        <UserDetailPage />
      </Wrapper>,
    );

    expect(await screen.findByText("Active")).toBeInTheDocument();
    expect(await screen.findByText("Verified")).toBeInTheDocument();
  });
});
