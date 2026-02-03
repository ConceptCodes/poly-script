import { render, screen } from "@testing-library/react";
import { BrowserRouter } from "react-router-dom";
import { describe, expect, it, vi } from "vitest";
import { AdminLayout } from "../AdminLayout";

vi.mock("../../store/auth", () => ({
  useAuthStore: vi.fn(() => ({
    hydrate: vi.fn(),
    adminEmail: "admin@polyscript.com",
    clear: vi.fn(),
  })),
}));

describe("AdminLayout", () => {
  it("renders navigation items", () => {
    render(
      <BrowserRouter>
        <AdminLayout />
      </BrowserRouter>,
    );

    expect(screen.getByText("Dashboard")).toBeInTheDocument();
    expect(screen.getByText("Users")).toBeInTheDocument();
    expect(screen.getByText("Teams")).toBeInTheDocument();
    expect(screen.getByText("Jobs")).toBeInTheDocument();
    expect(screen.getByText("Analytics")).toBeInTheDocument();
    expect(screen.getByText("Settings")).toBeInTheDocument();
    expect(screen.getByText("Audit Logs")).toBeInTheDocument();
  });

  it("renders admin email", () => {
    render(
      <BrowserRouter>
        <AdminLayout />
      </BrowserRouter>,
    );

    expect(screen.getByText("admin@polyscript.com")).toBeInTheDocument();
  });

  it("renders sign out button", () => {
    render(
      <BrowserRouter>
        <AdminLayout />
      </BrowserRouter>,
    );

    expect(screen.getByText("Sign out")).toBeInTheDocument();
  });
});
