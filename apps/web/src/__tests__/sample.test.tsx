import { render, screen } from "@testing-library/react";
import { BrowserRouter } from "react-router-dom";
import { describe, expect, it } from "vitest";

// Simple component to test
const TestComponent = () => <div>Test Content</div>;

describe("Test Infrastructure", () => {
  it("renders a simple component", () => {
    render(
      <BrowserRouter>
        <TestComponent />
      </BrowserRouter>,
    );
    expect(screen.getByText("Test Content")).toBeInTheDocument();
  });
});
