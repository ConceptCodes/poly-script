import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import { UserDetailPage } from "../UserDetailPage";
import { BrowserRouter, Routes, Route } from "react-router-dom";

vi.mock("../../lib/api", () => ({
  apiFetch: vi.fn().mockResolvedValue({
    id: "test-id",
    email: "test@example.com",
    full_name: "Test User",
    is_active: true,
    is_verified: true,
    is_suspended: false,
    created_at: new Date().toISOString(),
    teams: [],
  }),
}));

function Wrapper({ children }: { children: React.ReactNode }) {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/users/:id" element={children} />
      </Routes>
    </BrowserRouter>
  );
}

describe("UserDetailPage", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("renders user details title", () => {
    render(
      <Wrapper>
        <UserDetailPage />
      </Wrapper>,
    );
    expect(screen.getByText("User Details")).toBeInTheDocument();
  });

  it("renders account information section", async () => {
    render(
      <Wrapper>
        <UserDetailPage />
      </Wrapper>,
    );
    screen.getByText("Account Information");
    expect(screen.getByText("Email")).toBeInTheDocument();
    expect(screen.getByText("Full Name")).toBeInTheDocument();
    expect(screen.getByText("Created At")).toBeInTheDocument();
  });

  it("renders status & security section", async () => {
    render(
      <Wrapper>
        <UserDetailPage />
      </Wrapper>,
    );
    screen.getByText("Status & Security");
    expect(screen.getByText("Account Status")).toBeInTheDocument();
    expect(screen.getByText("Email Verified")).toBeInTheDocument();
    expect(screen.getByText("Suspended")).toBeInTheDocument();
  });
});
