import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@poly/ui";
import { useTranslation } from "react-i18next";
import type { OnboardingStepProps } from "./types";

// Adapt to flexible props to support OnboardingPage wiring
export function LanguageStep({ data, updateData }: OnboardingStepProps) {
  const { t } = useTranslation();

  const languages = [
    { code: "en", name: "English" },
    { code: "de", name: "Deutsch" },
    { code: "es", name: "Español" },
    { code: "fr", name: "Français" },
    { code: "jp", name: "日本語" },
  ];

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="text-2xl">{t("onboarding.language.title")}</CardTitle>
          <CardDescription>{t("onboarding.language.description")}</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            {languages.map((lang) => {
              const isSelected = data.language === lang.code;
              return (
                <button
                  key={lang.code}
                  type="button"
                  className={`relative rounded-lg border-2 p-6 cursor-pointer transition-all ${
                    isSelected
                      ? "border-primary bg-primary/5"
                      : "border-border hover:border-primary/50"
                  }`}
                  onClick={() => updateData("language", lang.code)}
                  aria-pressed={isSelected}
                >
                  <div className="flex items-center space-x-3">
                    <div className="text-3xl font-bold">{lang.code.toUpperCase()}</div>
                    <div className="text-sm">{lang.name}</div>
                  </div>
                  {isSelected && (
                    <div className="absolute top-2 right-2">
                      <div className="h-2 w-2 rounded-full bg-primary" />
                    </div>
                  )}
                </button>
              );
            })}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
