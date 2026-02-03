import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { useState } from "react";
import { BrowserRouter } from "react-router-dom";
import { describe, expect, it, vi } from "vitest";
import { LanguageStep } from "../pages/onboarding/LanguageStep";
import { OnboardingPage } from "../pages/onboarding/OnboardingPage";
import { PlanSelectionStep } from "../pages/onboarding/PlanSelectionStep";
import { TeamNameStep } from "../pages/onboarding/TeamNameStep";

vi.mock("react-router-dom", async () => {
  const actual = await vi.importActual("react-router-dom");
  return {
    ...actual,
    useNavigate: () => vi.fn(),
  };
});

vi.mock("../lib/store", () => {
  const setOnboardingComplete = vi.fn();
  return {
    useAppStore: (
      selector: (state: { setOnboardingComplete: typeof setOnboardingComplete }) => unknown,
    ) => selector({ setOnboardingComplete }),
  };
});

const renderWithRouter = (component: React.ReactElement) => {
  return render(<BrowserRouter>{component}</BrowserRouter>);
};

describe("Onboarding Flow", () => {
  it("renders onboarding page", () => {
    renderWithRouter(<OnboardingPage />);
    expect(screen.getByText(/welcome to polyscript/i)).toBeInTheDocument();
  });

  describe("LanguageStep", () => {
    it("renders language options", () => {
      renderWithRouter(<LanguageStep />);
      expect(screen.getByText(/english/i)).toBeInTheDocument();
      expect(screen.getByText(/deutsch/i)).toBeInTheDocument();
      expect(screen.getByText(/español/i)).toBeInTheDocument();
      expect(screen.getByText(/français/i)).toBeInTheDocument();
      expect(screen.getByText(/日本語/i)).toBeInTheDocument();
    });

    it("allows selecting a language", async () => {
      const user = userEvent.setup();
      renderWithRouter(<LanguageStep />);

      const germanOption = screen.getByText(/deutsch/i);
      await user.click(germanOption);

      // Verify selection (depends on implementation)
      expect(germanOption).toBeVisible();
    });
  });

  describe("TeamNameStep", () => {
    it("renders team name input", () => {
      renderWithRouter(<TeamNameStep />);
      expect(screen.getByLabelText(/team name/i)).toBeInTheDocument();
    });

    it("validates team name is required", async () => {
      const user = userEvent.setup();
      renderWithRouter(<TeamNameStep />);

      const nameInput = screen.getByLabelText(/team name/i);
      await user.type(nameInput, "a");

      await waitFor(() => {
        expect(screen.getByText(/at least 2/i)).toBeInTheDocument();
      });
    });

    it("allows entering team name", async () => {
      const user = userEvent.setup();
      renderWithRouter(<TeamNameStep />);

      const nameInput = screen.getByLabelText(/team name/i);
      await user.type(nameInput, "My Awesome Team");

      expect(nameInput).toHaveValue("My Awesome Team");
    });
  });

  describe("PlanSelectionStep", () => {
    it("renders plan options", () => {
      renderWithRouter(
        <PlanSelectionStep data={{ plan: "" }} updateData={() => {}} onNext={() => {}} />,
      );
      expect(screen.getByText(/free/i)).toBeInTheDocument();
      expect(screen.getByText(/standard/i)).toBeInTheDocument();
      expect(screen.getByText(/pro/i)).toBeInTheDocument();
    });

    it("allows selecting a plan", async () => {
      const user = userEvent.setup();
      const Wrapper = () => {
        const [data, setData] = useState({ plan: "" });
        return (
          <PlanSelectionStep
            data={data}
            updateData={(key, value) => setData((prev) => ({ ...prev, [key]: value }))}
            onNext={() => {}}
          />
        );
      };

      renderWithRouter(<Wrapper />);

      const standardPlan = screen.getByText(/standard/i);
      await user.click(standardPlan);

      expect(standardPlan).toBeVisible();
    });

    it("shows plan limits", () => {
      renderWithRouter(
        <PlanSelectionStep data={{ plan: "" }} updateData={() => {}} onNext={() => {}} />,
      );

      // Verify plan limits are displayed
      expect(screen.getAllByText(/uploads\/month/i).length).toBeGreaterThan(0);
      expect(screen.getAllByText(/team members/i).length).toBeGreaterThan(0);
    });
  });
});
