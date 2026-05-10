export type OnboardingData = {
  language: string;
  teamName: string;
  plan: string;
  members: string[];
};

export type UpdateOnboardingData = <K extends keyof OnboardingData>(
  key: K,
  value: OnboardingData[K],
) => void;

export type OnboardingStepProps = {
  data: OnboardingData;
  updateData: UpdateOnboardingData;
  onNext: () => void;
};
