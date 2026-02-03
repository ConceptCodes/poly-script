import { render, screen } from "@testing-library/react";
import { BrowserRouter } from "react-router-dom";
import { describe, expect, it, vi } from "vitest";
import { VerifyEmailCodePage } from "../pages/auth/VerifyEmailCodePage";

vi.mock("../lib/api", () => ({
  apiFetch: vi.fn(),
}));

describe("VerifyEmailCodePage", () => {
  it("should render verification form", () => {
    render(
      <BrowserRouter>
        <VerifyEmailCodePage />
      </BrowserRouter>,
    );

    expect(screen.getByPlaceholderText("123456")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /verify email/i })).toBeInTheDocument();
  });

  it("should show validation when code is less than 6 digits", async () => {
    render(
      <BrowserRouter>
        <VerifyEmailCodePage />
      </BrowserRouter>,
    );

    const submitButton = screen.getByRole("button", { name: /verify email/i });
    expect(submitButton).toBeDisabled();
  });
});
