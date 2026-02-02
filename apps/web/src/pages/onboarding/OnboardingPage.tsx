import { useState } from "react";
import { useTranslation } from "react-i18next";
import { CheckCircle2 } from "lucide-react";
import { Button } from "@poly/ui";
import { useNavigate } from "react-router-dom";
import { useAppStore } from "../../lib/store";
import { apiFetch } from "../../lib/api";
import { LanguageStep } from "./LanguageStep";
import { TeamNameStep } from "./TeamNameStep";
import { InviteMembersStep } from "./InviteMembersStep";
import { PlanSelectionStep } from "./PlanSelectionStep";
import { CompleteStep } from "./CompleteStep";

type DataType = {
  language: string;
  teamName: string;
  plan: string;
  members: string[];
};

export function OnboardingPage() {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const { setOnboardingComplete } = useAppStore((state) => ({
    setOnboardingComplete: state.setOnboardingComplete,
  }));

  const steps = [
    { id: "language", title: t("onboarding.steps.language") },
    { id: "teamName", title: t("onboarding.steps.teamName") },
    { id: "plan", title: t("onboarding.steps.plan") },
    { id: "inviteMembers", title: t("onboarding.steps.inviteMembers") },
    { id: "complete", title: t("onboarding.steps.complete") },
  ];

  const [currentStep, setCurrentStep] = useState(0);
  const [data, setData] = useState<DataType>({ 
    language: "", 
    teamName: "", 
    plan: "",
    members: [] 
  });

  const handleNext = () => {
    if (currentStep < steps.length - 1) {
      setCurrentStep(currentStep + 1);
    } else {
      handleComplete();
    }
  };

  const handleBack = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1);
    }
  };

  const handleComplete = async () => {
    try {
      await apiFetch("/v1/onboarding/complete", {
        method: "POST",
        body: {
          team_name: data.teamName,
          host_language: data.language,
          plan: data.plan || "FREE",
          invite_emails: data.members.filter((m) => m.length > 0),
        },
      });
      setOnboardingComplete(true);
      navigate("/dashboard");
    } catch (error) {
      console.error("Onboarding failed:", error);
    }
  };

  const updateData = <K extends keyof DataType>(key: K, value: DataType[K]) => {
    setData((prev) => ({ ...prev, [key]: value }));
  };

  const CurrentStepComponent: any = [
    LanguageStep, 
    TeamNameStep, 
    PlanSelectionStep,
    InviteMembersStep, 
    CompleteStep
  ][currentStep];

  return (
    <div className="min-h-screen bg-background py-8">
      <div className="container max-w-2xl mx-auto">
        <div className="mb-8">
          <h1 className="text-3xl font-bold">{t("onboarding.title")}</h1>
        </div>

        <div className="mb-8">
          {steps.map((step, index) => (
            <div
              key={step.id}
              className={`flex items-center ${index < currentStep ? "text-primary" : "text-muted-foreground"}`}
            >
              <div
                className={`flex items-center gap-2 ${index <= currentStep ? "opacity-100" : "opacity-50"}`}
              >
                {index < currentStep && <CheckCircle2 className="h-4 w-4" />}
                {step.title}
              </div>
              {index < steps.length - 1 && index !== currentStep && (
                <div className="flex-1 h-0.5 bg-primary" />
              )}
            </div>
          ))}
        </div>

        <div className="flex justify-between items-center mb-6">
          <Button variant="outline" onClick={handleBack} disabled={currentStep === 0}>
            {t("onboarding.back")}
          </Button>
          <Button onClick={handleNext}>
            {currentStep === steps.length - 1 ? t("onboarding.completeCta") : t("onboarding.next")}
          </Button>
        </div>

        <CurrentStepComponent data={data} updateData={updateData as any} onNext={handleNext} />
      </div>
    </div>
  );
}
